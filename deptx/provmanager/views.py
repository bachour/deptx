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

@staff_member_required    
def index(request):
    
    provenance_list = Provenance.objects.all().order_by("-modifiedAt")
    
    return render(request, 'provmanager/index.html', {'provenance_list':provenance_list})

@staff_member_required
def view(request, id):
    provenance = Provenance.objects.get(id=id)
    json_str = getProvJsonStr(provenance)
    
    return render(request, 'provmanager/view.html', {'provenance': provenance, 'json':json_str})

@staff_member_required
def view_randomize(request, id):
    provenance = Provenance.objects.get(id=id)
    json_str = getProvJsonStr(provenance)
    
    random_graph = get_random_graph(json.loads(json_str))
    inconsistencies_list, clean_graph = get_inconsistencies(random_graph)

    request.session['attribute1'] = json.dumps(inconsistencies_list[0])
    request.session['attribute2'] = json.dumps(inconsistencies_list[1])
    request.session['prov_id'] = provenance.id
    
            
    return render(request, 'provmanager/view_randomize.html', {'provenance_name':provenance.name, 'provenance_store_id':provenance.store_id, 'json_str':json.dumps(clean_graph) })

@staff_member_required
def create(request):
    if request.method == 'POST':
        if 'convert' in request.POST or 'randomize' in request.POST:
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
                
            if 'randomize' in request.POST:
                json_str = json.dumps(get_random_graph(json.loads(json_str)))
            
            return render_to_response('provmanager/create.html', {"output_list":output_list, "filename":filename, "graphml_str": graphml_str, "json_str": json_str, "valid":valid, "validation_url":validation_url}, context_instance=RequestContext(request))

        elif 'save' in request.POST:
            graphml_str = request.POST["graphml"]
            provn_str, output = convert_graphml_string(graphml_str)
            valid, validation_url = validate(provn_str)
            if valid:
                name = request.POST["filename"]
                if name=="":
                    name = "PLEASE ENTER A NAME"
                
                inconsistencies_list, clean_graph = get_inconsistencies(json.loads(provn_str.get_provjson()))

                if inconsistencies_list:
                    attribute1 = json.dumps(inconsistencies_list[0])
                    attribute2 = json.dumps(inconsistencies_list[1])
                    type = Provenance.TYPE_CRON
                else:
                    attribute1 = None
                    attribute2 = None
                    #TODO: is there a better way to check the type?
                    #if there are no inconsistencies, then we assume it is a MOP_TEMPLATE provenance document
                    type = Provenance.TYPE_MOP_TEMPLATE
  
                bundle = ProvBundle.from_provjson(json.dumps(clean_graph))
                
                store_id = API.submit_document(bundle, name, public=False)

                provenance = Provenance(name=name, store_id=store_id, attribute1=attribute1, attribute2=attribute2, type=type)
                provenance.save()
                return HttpResponseRedirect(reverse('provmanager_index'))
            
            
    return render_to_response('provmanager/create.html', context_instance=RequestContext(request))

def randomize_task(task, mop):
    #bundle = API.get_document(task.provenance.store_id)
    #TODO randomize provn/json
    json_graph = getProvJson(task.provenance)
    random_graph = get_random_graph(json_graph)
    inconsistencies_list, clean_graph = get_inconsistencies(random_graph)

    attribute1 = json.dumps(inconsistencies_list[0])
    attribute2 = json.dumps(inconsistencies_list[1])

    bundle = ProvBundle.from_provjson(json.dumps(clean_graph))
    name = "%s (randomized for %s)" % (task.name, mop.user.username)
    store_id = API.submit_document(bundle, name, public=False)
    provenance = Provenance(name=name, store_id=store_id, attribute1=attribute1, attribute2=attribute2, type=Provenance.TYPE_MOP_INSTANCE)
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

def improve_saved_state(request, serial):
    provenance = Provenance.objects.get(serial=serial)
    if provenance.type == Provenance.TYPE_CRON:
            documentInstance = CronDocumentInstance.objects.get(document=provenance.document, cron=request.user.cron)
    elif provenance.type == Provenance.TYPE_MOP_INSTANCE:
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
        post_node1 = request.POST.get('node1', "")
        post_node2 = request.POST.get('node2', "")
        post_attribute1 = request.POST.get('attribute1', "")
        post_attribute2 = request.POST.get('attribute2', "")
        is_test = json.loads(request.POST.get('is_test', False))
        
        player_attribute1 = makeAttributeString(post_node1, post_attribute1)
        player_attribute2 = makeAttributeString(post_node2, post_attribute2)
        
        try:
            provenance = Provenance.objects.get(serial=serial)
            if provenance.attribute1 is not None and provenance.attribute2 is not None: 
                attribute1_json = json.loads(provenance.attribute1)
                attribute2_json = json.loads(provenance.attribute2)
            else:
                attribute1_json = []
                attribute2_json = []
        #if we have no proper serial in the post, then we are probably looking at a randomized MOP_TEMPLATE
        except Provenance.DoesNotExist:
            provenance = Provenance.objects.get(id=request.session['prov_id'])
            attribute1_json = json.loads(request.session['attribute1'])
            attribute2_json = json.loads(request.session['attribute2'])
            print 'got stuff from the session cookie'
        
        stored_attribute1_list = []
        stored_attribute2_list = []
        
        for a_json in attribute1_json:
            stored_attribute1_list.append(makeAttributeString(a_json['node'], a_json['attribute']))
        for a_json in attribute2_json:
            stored_attribute2_list.append(makeAttributeString(a_json['node'], a_json['attribute']))
        
        if player_attribute1 in stored_attribute1_list and player_attribute2 in stored_attribute2_list:
            correct = True
        elif player_attribute1 in stored_attribute2_list and player_attribute2 in stored_attribute1_list:
            correct = True
       
        if is_test and request.user.is_staff:
            if correct:
                message = "Test feedback: Yes, this is where the inconsistency is!"
            else:
                message = "Test feedback: No, this is not correct."
            close_prov = False
        else:
            if provenance.type == Provenance.TYPE_CRON:
                if correct:
                    message = "You found the suspicious data! Great job, proceed to your debrief."
                    #TODO check properly for cron-user and if Instance exists
                    cronDocumentInstance = CronDocumentInstance.objects.get(document=provenance.document, cron=request.user.cron)
                    cronDocumentInstance.solved = True
                    cronDocumentInstance.save()
                    close_prov = True
                else:
                    message = "The data you submitted does not seem suspicious. Please keep investigating."
                    close_prov = False
                  
            elif provenance.type == Provenance.TYPE_MOP_INSTANCE:
                message = "Provenance modification saved. Please submit document now."  
                #TODO check properly for mop-user and if Instance exists
                documentInstance = DocumentInstance.objects.get(taskInstance=provenance.taskInstance, mop=request.user.mop)
                documentInstance.modified = True
                documentInstance.correct = correct
                documentInstance.save()
                close_prov = True

        
        json_data = json.dumps({"close_prov":close_prov, "message":message})

        return HttpResponse(json_data, mimetype="application/json")


def makeAttributeString(node, attribute):
    return node + "." + attribute

@csrf_exempt
def prov_log_action(request):
    #TODO better error handling and feedback
    correct = False
    message = "This is not correct."

    #if request.is_ajax():
    if request.method == 'POST':
        serial = request.POST.get('serial', None)
        action = request.POST.get('action', None) #'move' or 'click'
        node = request.POST.get('node', None)
        x = request.POST.get('x', None)
        y = request.POST.get('y', None)
        attribute = request.POST.get('attribute', None)
        state = request.POST.get('state', None)
        
        #TODO log everything, including clicking
        provenance = Provenance.objects.get(serial=serial)
        if provenance.type == Provenance.TYPE_CRON:
            documentInstance = CronDocumentInstance.objects.get(document=provenance.document, cron=request.user.cron)
        elif provenance.type == Provenance.TYPE_MOP_INSTANCE:
            documentInstance = DocumentInstance.objects.get(taskInstance=provenance.taskInstance, mop=request.user.mop)
        else:
            message = "no document instance found"
            error = True
        
        if documentInstance is not None:
        
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
                message = 'position updated'
                error = False
            
            elif action == 'click':
                #TODO log clicking
                message = 'click registered but not yet stored'
                error = False

        json_data = json.dumps({"message":message, "error":error})            
        return HttpResponse("json_data", mimetype="application/json") 
        
  