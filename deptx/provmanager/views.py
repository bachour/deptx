from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext

from provmanager.wrapper import Api
from provmanager.models import Provenance, ProvenanceLog
from prov.model import ProvBundle, Namespace

from deptx.secrets import api_username, api_key
from assets.models import Document, Task
from cron.models import CronDocumentInstance
from mop.models import DocumentInstance, TaskInstance


from django.views.decorators.csrf import csrf_exempt
from deptx.helpers import now, generateUUID
from provmanager.utility_scripts import get_random_graph, get_inconsistencies



import json

from graphml2prov import convert_graphml_string, validate
import prov.model

api_location="https://provenance.ecs.soton.ac.uk/store/api/v0/"

API = Api(api_location=api_location, api_username=api_username, api_key=api_key)
MODE_CRON = "cron"
MODE_MOP = "mop"


@staff_member_required    
def index(request):
    
    provenance_list = Provenance.objects.all().order_by("-modifiedAt")
    
    return render(request, 'provmanager/index.html', {'provenance_list':provenance_list})

@staff_member_required
def view(request, id):
    provenance = Provenance.objects.get(id=id)
    bundle = API.get_document(provenance.store_id)
    #svg = getProvSvg(provenance)
    #xml = api.get_document(provenance.store_id, format="xml")
    json_str = getProvJsonStr(provenance)
    
    #TODO fix mode
    return render(request, 'provmanager/view.html', {'provenance': provenance, 'bundle':bundle, 'json':json_str, 'mode':MODE_CRON})
    #return render(request, 'provmanager/improve.html', {'provenance': provenance})

@staff_member_required
def create(request):
    if request.method == 'POST':
        if 'convert' in request.POST:
            graphml_str = request.POST["graphml"]
            filename = request.POST["filename"]
            provn_str, output = convert_graphml_string(graphml_str)
            output_list = output.splitlines()
            output_list.sort()
            
            
            valid, validation_url = validate(provn_str)
            if valid:
                json_str = provn_str.get_provjson()
            else:
                json_str={}
            return render_to_response('provmanager/create.html', {"is_test":True, "output_list":output_list, "filename":filename, "graphml_str": graphml_str, "json_str": json_str, "valid":valid, "validation_url":validation_url}, context_instance=RequestContext(request))
        elif 'save' in request.POST:
            graphml_str = request.POST["graphml"]
            provn_str = convert_graphml_string(graphml_str)
            valid, validation_url = validate(provn_str)
            if valid:
                name = request.POST["filename"]
                if name=="":
                    name = "PLEASE ENTER A NAME"
                store_id = API.submit_document(provn_str, name, public=False)
                provenance = Provenance(name=name, store_id=store_id)
                provenance.save()
                return HttpResponseRedirect(reverse('provmanager_index'))
            
            
    return render_to_response('provmanager/create.html', context_instance=RequestContext(request))

def randomize_task(task, mop):
    #bundle = API.get_document(task.provenance.store_id)
    #TODO randomize provn/json
    json_graph = getProvJson(task.provenance)
    random_graph = get_random_graph(json_graph)
    #inconsistencies = get_inconsistencies(random_graph)
    bundle = ProvBundle.from_provjson(json.dumps(random_graph))
    name = "%s (randomized for %s)" % (task.name, mop.user.username)
    store_id = API.submit_document(bundle, name, public=False)
    provenance = Provenance(name=name, store_id=store_id)
    provenance.save()

    taskInstance = TaskInstance.objects.create(mop=mop, task=task, provenance=provenance)
    return taskInstance

@staff_member_required
def convert(request, id):
    provenance = Provenance.objects.get(id=id)
    convert_graphml_string(provenance.graphml)

def getProvJsonStr(provenance):
    json_str = API.get_document(provenance.store_id, format="json")
    parsed = json.loads(json_str)
    return json.dumps(parsed, indent=4, sort_keys=True)

def getProvJson(provenance):
    json_str = API.get_document(provenance.store_id, format="json")
    return json.loads(json_str)


def getProvSvg(provenance):
    svg = API.get_document(provenance.store_id, format="svg")
    return svg

def improve(request, serial):
    provenance = Provenance.objects.get(serial=serial)
    json_str = getProvJsonStr(provenance)
    return HttpResponse(json_str, content_type="application/json")

def improve_saved_state(request, serial, mode):
    provenance = Provenance.objects.get(serial=serial)
    if mode == MODE_CRON:
            documentInstance = CronDocumentInstance.objects.get(document=provenance.document, cron=request.user.cron)
    elif mode == MODE_MOP:
            documentInstance = DocumentInstance.objects.get(taskInstance=provenance.taskInstance, mop=request.user.mop)
    try:
        json_load = json.loads(documentInstance.provenanceState)
        json_str = json.dumps(json_load, indent=4, sort_keys=True)
    except:
        json_str = '[]'
    return HttpResponse(json_str, content_type="application/json")


#TODO check if logged in as cron/mop
@csrf_exempt
def prov_check(request):
    
    correct = False
    message = "This is not correct."

    #if request.is_ajax():
    if request.method == 'POST':
        serial = request.POST.get('serial', "")
        node1 = request.POST.get('node1', "")
        node2 = request.POST.get('node2', "")
        attribute1 = request.POST.get('attribute1', "")
        attribute2 = request.POST.get('attribute2', "")
        mode = request.POST.get('mode', "")
        
        try:
            provenance = Provenance.objects.get(serial=serial)
        except Provenance.DoesNotExist:
            print "bad provenance store_id"
        
        
        
        if provenance.node1 == node1 and provenance.node2 == node2 and provenance.attribute1 == attribute1 and provenance.attribute2 == attribute2:
            correct = True
        elif provenance.node2 == node1 and provenance.node1 == node2 and provenance.attribute2 == attribute1 and provenance.attribute1 == attribute2:
            correct = True
        

        if mode == MODE_CRON:
            if correct:
                message = "You found the suspicious data! Great job, proceed to your debrief."

                #TODO check properly for cron-user and if Instance exists
                cronDocumentInstance = CronDocumentInstance.objects.get(document=provenance.document, cron=request.user.cron)
                cronDocumentInstance.solved = True
                cronDocumentInstance.save()
            else:
                message = "The data you submitted does not seem suspicious. Please keep investigating."
                  
        elif mode == MODE_MOP:
            message = "Provenance modification saved. Please submit document now."  
            #TODO check properly for mop-user and if Instance exists
            documentInstance = DocumentInstance.objects.get(taskInstance=provenance.taskInstance, mop=request.user.mop)
            documentInstance.modified = True
            documentInstance.correct = correct
            documentInstance.save()
            correct = True
            
        
        json_data = json.dumps({"correct":correct, "message":message})

        return HttpResponse(json_data, mimetype="application/json")

@csrf_exempt
def prov_log_action(request):
    #TODO better error handling and feedback
    correct = False
    message = "This is not correct."

    #if request.is_ajax():
    if request.method == 'POST':
        serial = request.POST.get('serial', None)
        mode = request.POST.get('mode', None) #MODE_MOP or MODE_CRON
        action = request.POST.get('action', None) #'move' or 'click'
        node = request.POST.get('node', None)
        x = request.POST.get('x', None)
        y = request.POST.get('y', None)
        attribute = request.POST.get('attribute', None)
        state = request.POST.get('state', None)
        
        #TODO log everything, including clicking
        provenance = Provenance.objects.get(serial=serial)
        if mode == MODE_CRON:
            documentInstance = CronDocumentInstance.objects.get(document=provenance.document, cron=request.user.cron)
        elif mode == MODE_MOP:
            documentInstance = DocumentInstance.objects.get(taskInstance=provenance.taskInstance, mop=request.user.mop)
        
        if action == 'move':
            try:
                stored_data = json.loads(documentInstance.provenanceState)
            except:
                stored_data = []
            updated = False
            for data in stored_data:
                if data['node'] == node:
                    print 'equal'
                    data['x'] = x
                    data['y'] = y
                    updated = True
                    break
            if not updated:
                stored_data.append({"node":node, "x":x, "y":y})
            documentInstance.provenanceState = json.dumps(stored_data)
            documentInstance.save()
            #documentInstance.provenanceState += json_data
            #documentInstance.save()
        elif action == 'click':
            pass
        
        return HttpResponse("json_data", mimetype="application/json") 
        
  