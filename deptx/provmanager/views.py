from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from provmanager.wrapper import Api
from provmanager.models import Provenance
from prov.model import ProvBundle, Namespace

from deptx.secrets import api_username, api_key
from cron.models import CronDocumentInstance
from mop.models import MopDocumentInstance, RandomizedDocument
from assets.models import CronDocument


from django.views.decorators.csrf import csrf_exempt
from deptx.helpers import now, generateUUID
from provmanager.utility_scripts import get_random_graph, get_inconsistencies
from deptx.settings import MEDIA_URL
from mop import tutorial
import urllib2

import json

from graphml2prov import convert_graphml_string, validate
import prov.model
from logger.models import ProvLog, ActionLog
from logger import logging
from players.models import Cron
from provmanager import provstore_settings


API = Api(api_location=provstore_settings.api_location, api_username=api_username, api_key=api_key)

@staff_member_required    
def index(request):
    
    provenance_list = Provenance.objects.exclude(type=Provenance.TYPE_MOP_INSTANCE).order_by("type", "-modifiedAt")
    
    return render(request, 'provmanager/index.html', {'provenance_list':provenance_list, 'PROVSTORE_URL':provstore_settings.api_documents})

@staff_member_required    
def index_instances(request):
    
    provenance_list = Provenance.objects.filter(type=Provenance.TYPE_MOP_INSTANCE).order_by("type", "-modifiedAt")
    
    return render(request, 'provmanager/index.html', {'provenance_list':provenance_list, 'PROVSTORE_URL':provstore_settings.api_documents})



@staff_member_required
def view(request, id):
    provenance = Provenance.objects.get(id=id)
    json_str = getProvJsonStr(provenance)
    
    try:
        guide = provenance.document.guide
    except:
        try:
            guide = provenance.randomizedDocument.mopDocument.guide
        except:
            guide = None
    
    return render(request, 'provmanager/view.html', {'provenance': provenance, 'json':json_str, 'guide':guide})

@staff_member_required
def view_randomize(request, id):
    provenance = Provenance.objects.get(id=id)
    json_str = getProvJsonStr(provenance)
    
    random_graph = get_random_graph(json.loads(json_str))
    inconsistencies_list, clean_graph = get_inconsistencies(random_graph)
    
    if inconsistencies_list:
        request.session['attribute1'] = json.dumps(inconsistencies_list[0])
        request.session['attribute2'] = json.dumps(inconsistencies_list[1])
    else:
        request.session['attribute1'] = None
        request.session['attribute2'] = None
    request.session['prov_id'] = provenance.id
    
    try:
        guide = provenance.document.guide
    except:
        guide = None
        
    json_str = json.dumps(clean_graph, sort_keys=True, indent=4, separators=(',', ': '))
    return render(request, 'provmanager/view_randomize.html', {'inconsistencies_list':inconsistencies_list, 'provenance_name':provenance.name, 'provenance_store_id':provenance.store_id, 'json_str':json_str, 'guide':guide })


def getStuff(request):
    filename = request.POST["filename"]
    request.session['filename'] = filename
    full = "http://univeam1.miniserver.com/media/PROVENANCE/test/%s" % (filename)
    response = urllib2.urlopen(full)
    content = response.read()
    response.close()
    return filename, content

@staff_member_required
def create(request):
    if request.method == 'POST':
        if 'convertMop' in request.POST or 'convertCron' in request.POST or 'randomize' in request.POST:
            if 'convertCron' in request.POST:
                isCron = True
                isMop = False
            else:
                isCron = False
                isMop = True
            #graphml_str = request.POST["graphml"]
            filename, graphml_str = getStuff(request)
            
            
            provn_str, output = convert_graphml_string(graphml_str)
            output_list = output.splitlines()
            output_list.sort()

            valid = True
            validation_url = "bla"
            #valid, validation_url = validate(provn_str)
            if valid:
                json_str = provn_str.get_provjson()
            else:
                json_str={}
            
            #print json_str
                
            inconsistencies_list = None
            spoilers = False
            if 'randomize' in request.POST:
                print request.POST
                random_graph = get_random_graph(json.loads(json_str))
                json_str = json.dumps(random_graph)
                inconsistencies_list, clean_graph = get_inconsistencies(random_graph)
                if 'spoilers' in request.POST: 
                    spoilers = True
                else:
                    spoilers = False
                    json_str = json.dumps(clean_graph)
                print spoilers
                
                
            return render(request, 'provmanager/create.html', {"inconsistencies_list":inconsistencies_list, "spoilers":spoilers, "output_list":output_list, "filename":filename, "json_str": json_str, "isMop":isMop, "isCron":isCron, "valid":valid, "validation_url":validation_url})

        elif 'saveMop' in request.POST or 'saveCron' in request.POST:
            if 'saveCron' in request.POST:
                type = Provenance.TYPE_CRON
            else:
                type = Provenance.TYPE_MOP_TEMPLATE
            
            filename, graphml_str = getStuff(request)
            provn_str, output = convert_graphml_string(graphml_str)
            
            valid = True
            validation_url = "bla"
            #valid, validation_url = validate(provn_str)
            if valid:
                name = request.POST["filename"]
                if name=="":
                    name = "PLEASE ENTER A NAME"
                
                inconsistencies_list, clean_graph = get_inconsistencies(json.loads(provn_str.get_provjson()))

                if inconsistencies_list:
                    attribute1 = json.dumps(inconsistencies_list[0])
                    attribute2 = json.dumps(inconsistencies_list[1])
                else:
                    attribute1 = None
                    attribute2 = None
  
                bundle = ProvBundle.from_provjson(json.dumps(clean_graph))
                
                store_id = API.submit_document(bundle, name, public=False)

                provenance = Provenance(name=name, store_id=store_id, attribute1=attribute1, attribute2=attribute2, type=type)
                provenance.save()
                return HttpResponseRedirect(reverse('provmanager_index'))
            
    try:
        filename = request.session['filename']
    except:
        filename = ""      
    return render(request, 'provmanager/create.html', {"filename":filename})

def randomize_document(mopDocument):
    #bundle = API.get_document(task.provenance.store_id)
    #TODO randomize provn/json
    json_graph = getProvJson(mopDocument.provenance)
    random_graph = get_random_graph(json_graph)
    inconsistencies_list, clean_graph = get_inconsistencies(random_graph)

    try:
        attribute1 = json.dumps(inconsistencies_list[0])
        attribute2 = json.dumps(inconsistencies_list[1])
    except:
        attribute1 = None
        attribute2 = None

    bundle = ProvBundle.from_provjson(json.dumps(clean_graph))
    name = "%s (randomized)" % (mopDocument.provenance.name)
    store_id = API.submit_document(bundle, name, public=False)
    provenance = Provenance(name=name, store_id=store_id, attribute1=attribute1, attribute2=attribute2, type=Provenance.TYPE_MOP_INSTANCE)
    provenance.save()
        
    randomizedDocument = RandomizedDocument.objects.create(mopDocument=mopDocument, provenance=provenance)
    return randomizedDocument

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
        try:
            cronDocument = CronDocument.objects.get(provenance=provenance)
            documentInstance = CronDocumentInstance.objects.get(cronDocument=cronDocument, cron=request.user.cron)
        except:
            pass
    elif provenance.type == Provenance.TYPE_MOP_INSTANCE:
            try:
                randomizedDocument = RandomizedDocument.objects.get(provenance=provenance)
                documentInstance = MopDocumentInstance.objects.get(randomizedDocument=randomizedDocument, mop=request.user.mop)
            except:
                pass
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
    status = "ok"
    
    if not request.user.is_active:
        json_data = json.dumps({"message":"You are currently not logged in. Please login to continue.", "status":"logged_out"})            
        return HttpResponse(json_data, mimetype="application/json")

    #if request.is_ajax():
    if request.method == 'POST':
        serial = request.POST.get('serial', "")
        post_node1 = request.POST.get('node1', "")
        post_node2 = request.POST.get('node2', "")
        post_attribute1 = request.POST.get('attribute1', "")
        post_attribute2 = request.POST.get('attribute2', "")
        is_empty = json.loads(request.POST.get('is_empty', False))
        is_test = json.loads(request.POST.get('is_test', False))
        
        player_attribute1 = makeAttributeString(post_node1, post_attribute1)
        player_attribute2 = makeAttributeString(post_node2, post_attribute2)
        
        try:
            provenance = Provenance.objects.get(serial=serial)
            try: 
                attribute1_json = json.loads(provenance.attribute1)
                attribute2_json = json.loads(provenance.attribute2)
            except:
                attribute1_json = []
                attribute2_json = []
        #if we have no proper serial in the post, then we are probably looking at a randomized MOP_TEMPLATE
        except Provenance.DoesNotExist:
            provenance = Provenance.objects.get(id=request.session['prov_id'])
            try:
                attribute1_json = json.loads(request.session['attribute1'])
                attribute2_json = json.loads(request.session['attribute2'])
            except:
                attribute1_json = None
                attribute2_json = None
                
            print 'got stuff from the session cookie'
        
        stored_attribute1_list = []
        stored_attribute2_list = []
        
        if provenance.attribute1 is None and provenance.attribute2 is None:
            if is_empty:
                correct = True
        
        else:
            for a_json in attribute1_json:
                stored_attribute1_list.append(makeAttributeString(a_json['node'], a_json['attribute']))
            for a_json in attribute2_json:
                stored_attribute2_list.append(makeAttributeString(a_json['node'], a_json['attribute']))
            
            if player_attribute1 in stored_attribute1_list and player_attribute2 in stored_attribute2_list:
                correct = True
            elif player_attribute1 in stored_attribute2_list and player_attribute2 in stored_attribute1_list:
                correct = True
       
        stars = None
        if is_test and request.user.is_staff:
            if correct:
                message = "Test feedback: Yes, this is where the inconsistency is!"
            else:
                message = "Test feedback: No, this is not correct."
            close_prov = False
        else:
            cronDocumentInstance = None
            mopDocumentInstance = None
            if provenance.type == Provenance.TYPE_CRON:
                #TODO check properly for cron-user and if Instance exists
                cronDocumentInstance = CronDocumentInstance.objects.get(cronDocument=provenance.document, cron=request.user.cron)
                logging.log_action(ActionLog.ACTION_CRON_PROVENANCE_SUBMIT, cron=cronDocumentInstance.cron, cronDocumentInstance=cronDocumentInstance, cronDocumentInstanceCorrect=correct)
                if correct:
                    cronDocumentInstance.solved = True
                    cronDocumentInstance.save()
                    close_prov = True
                    stars = cronDocumentInstance.getStars()
                    attempts = cronDocumentInstance.failedAttempts + 1
                    
                    if stars == 3:
                        message = "Excellent job! This will be reflected in your agent profile."
                    elif stars == 2:
                        message = "It took you %s tries, but good job anyway. Your agent profile has been updated." % attempts
                    elif stars == 1:
                        message = "Yes, you did it. It did take %s attempts, but the result is what counts. Your success has been logged in your agent profile." % attempts
                    
                    
                else:
                    cronDocumentInstance.increaseFailedAttempts()
                    close_prov = False
                    if cronDocumentInstance.failedAttempts >= 50:
                        message = "Yeah. Not it."
                    elif cronDocumentInstance.failedAttempts >= 30:
                        message = "Honestly, now you are just guessing, right? Contact HQ, they might have uncovered an additional clue!"
                    elif cronDocumentInstance.failedAttempts >= 10:
                        message = "You are trying very hard, but this is not it. Maybe send a message to HQ to see if they have more intel."
                    elif is_empty:
                        message = "No, we are pretty sure that something is wrong with this data. Please keep investigating."
                    else:
                        message = "The data you submitted does not seem suspicious. Please keep investigating."
                    
                  
            elif provenance.type == Provenance.TYPE_MOP_INSTANCE:
                message = "Provenance modification saved. Please submit document now."  
                #TODO check properly for mop-user and if Instance exists
                mopDocumentInstance = MopDocumentInstance.objects.get(randomizedDocument=provenance.randomizedDocument, mop=request.user.mop)
                mopDocumentInstance.modified = True
                mopDocumentInstance.correct = correct
                mopDocumentInstance.save()
                logging.log_action(ActionLog.ACTION_MOP_PROVENANCE_SUBMIT, mop=mopDocumentInstance.mop, mopDocumentInstance=mopDocumentInstance, mopDocumentInstanceCorrect=correct)
                tutorial.checkProvenance(mopDocumentInstance.mop.mopTracker, mopDocumentInstance.correct)
                close_prov = True
            logging.log_prov(action=ProvLog.ACTION_SUBMIT, cronDocumentInstance=cronDocumentInstance, mopDocumentInstance=mopDocumentInstance, node1=post_node1, node2=post_node2, attribute1=post_attribute1, attribute2=post_attribute2, empty=is_empty, correct=correct)

        
        json_data = json.dumps({"close_prov":close_prov, "status":status, "message":message, "stars":stars})

        return HttpResponse(json_data, mimetype="application/json")


def makeAttributeString(node, attribute):
    return node + "." + attribute

@csrf_exempt
def prov_log_action(request):
    #TODO better error handling and feedback
    status = "ok"
    message = "This is not correct."
    
    if not request.user.is_active:
        json_data = json.dumps({"message":"You are currently not logged in. Please login to continue.", "status":"logged_out"})            
        return HttpResponse(json_data, mimetype="application/json")
    
    #if request.is_ajax():
    if request.method == 'POST':
        serial = request.POST.get('serial', None)
        action = request.POST.get('action', None) #'move' or 'click'
        node = request.POST.get('node', None)
        x = request.POST.get('x', None)
        y = request.POST.get('y', None)
        attribute = request.POST.get('attribute', None)
        position = request.POST.get('position', None)
        inactive = json.loads(request.POST.get('inactive', None))
        if attribute == "none":
            attribute = None
        try:
            state = json.loads(request.POST.get('state', None))
        except:
            state = None
        
        #TODO log everything, including clicking
        cronDocumentInstance = None
        mopDocumentInstance = None
        provenance = Provenance.objects.get(serial=serial)
        if provenance.type == Provenance.TYPE_CRON:
            documentInstance = CronDocumentInstance.objects.get(cronDocument=provenance.document, cron=request.user.cron)
            cronDocumentInstance = documentInstance
            if cronDocumentInstance.cronDocument.autoSolve:
                inactive = False
        elif provenance.type == Provenance.TYPE_MOP_INSTANCE:
            documentInstance = MopDocumentInstance.objects.get(randomizedDocument=provenance.randomizedDocument, mop=request.user.mop)
            mopDocumentInstance = documentInstance
        else:
            message = "no document instance found"
            error = True
        
        if documentInstance is not None:
            try:
                stored_data = json.loads(documentInstance.provenanceState)
            except:
                stored_data = []
            
            updated = False
            if action == 'move':
                if not inactive:
                    for data in stored_data:
                        try:
                            if data['node'] == node:
                                data['x'] = x
                                data['y'] = y
                                updated = True
                                break
                        except:
                            pass
                    if not updated:
                        stored_data.append({"node":node, "x":x, "y":y})
                    documentInstance.provenanceState = json.dumps(stored_data)
                    documentInstance.save()
                    message = 'position updated'
                else:
                    message = 'position ignored as is inactive'
                error = False
                logAction = ProvLog.ACTION_MOVE
                
            
            elif action == 'click':
                if attribute == 'mop:__url':
                    message = 'media opened registered'
                    error = False
                    logAction = ProvLog.ACTION_MEDIA
                else:    
                    if not inactive:
                        for data in stored_data:
                            try:
                                if data['position'] == position:
                                    if state and attribute is not None:
                                        data['selected_node'] = node
                                        data['selected_attribute'] = attribute
                                        updated = True
                                        break
                                    elif state and attribute is None:
                                        data['selected_node'] = node
                                        data['selected_attribute'] = None
                                        updated = True
                                        break
                                    elif not state and attribute is not None:
                                        data['selected_node'] = node
                                        data['selected_attribute'] = None
                                        updated = True
                                        break
                                    elif not state and attribute is None:
                                        data['selected_node'] = None
                                        data['selected_attribute'] = None
                                        updated = True
                                        break
                            except:
                                pass
                        if not updated:
                            stored_data.append({"position":position, "selected_node":node, "selected_attribute":attribute})
                        documentInstance.provenanceState = json.dumps(stored_data)
                        documentInstance.save()
                        message = 'click registered'
                    else:
                        message = 'click ignored as is inactive'
                    error = False
                    logAction = ProvLog.ACTION_CLICK
            logging.log_prov(action=logAction, cronDocumentInstance=cronDocumentInstance, mopDocumentInstance=mopDocumentInstance, node1=node, attribute1=attribute, x=x, y=y, selected=state, inactive=inactive)
        
        if error:
            status = "error"
        json_data = json.dumps({"message":message, "status":status})            
        return HttpResponse(json_data, mimetype="application/json") 
        
