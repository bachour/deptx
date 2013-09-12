from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from provmanager.wrapper import Api
from provmanager.models import Provenance
from prov.model import ProvBundle

from deptx.api import api_location, api_username, api_key
from assets.models import Document

from django.views.decorators.csrf import csrf_exempt


import json

from graphml2prov import convert_graphml

api = Api(api_location=api_location, api_username=api_username, api_key=api_key)


#TODO make everything unacessible for non-admin users (apart from improve)    
def index(request):
    provenance_list = Provenance.objects.all()
    
    for provenance in provenance_list:
        provenance.cron_document_list = Document.objects.filter(provenance=provenance).exclude(case__isnull=True)
        provenance.mop_document_list = Document.objects.filter(provenance=provenance).exclude(task__isnull=True)
    
    return render(request, 'provmanager/index.html', {'provenance_list':provenance_list})

def view(request, id):
    provenance = Provenance.objects.get(id=id)
    bundle = api.get_document(provenance.store_id)
    svg = getProvSvg(provenance)
    #xml = api.get_document(provenance.store_id, format="xml")
    json_str = getProvJson(provenance)

    return render(request, 'provmanager/view.html', {'provenance': provenance, 'bundle':bundle, 'json':json_str, 'svg':svg})
    #return render(request, 'provmanager/improve.html', {'provenance': provenance})


def create(request):
    json_str = api.get_document(212, format="json")
    return render_to_response('provmanager/create.html', {"json_str": json_str})

def convert(request, id):
    provenance = Provenance.objects.get(id=id)
    convert_graphml(provenance.graphml)
    return HttpResponseRedirect(reverse('provmanager_index'))

#def create(request):
    #name = "random name"
    #bundle = ProvBundle()
    #bundle.entity('crashed_car')
    #store_id = api.submit_document(bundle, name, public=False)
    
    #provenance = Provenance(store_id=store_id, name=name)
    #provenance.save()
    #return HttpResponseRedirect(reverse('provmanager_index'))

def getProvJson(provenance):
    json_str = api.get_document(provenance.store_id, format="json")
    parsed = json.loads(json_str)
    return json.dumps(parsed, indent=4, sort_keys=True)

def getProvSvg(provenance):
    svg = api.get_document(provenance.store_id, format="svg")
    return svg

def improve(request, serial):
    provenance = Provenance.objects.get(serial=serial)
    json_str = getProvJson(provenance)
    return HttpResponse(json_str, content_type="application/json")


#TODO check if logged in as cron
@csrf_exempt
def cron_submit(request):
    correct = False
    message = "This is not correct."
    #if request.is_ajax():
    if request.method == 'POST':
        serial = request.POST.get('serial', "")
        node1 = request.POST.get('node1', "")
        node2 = request.POST.get('node2', "")
        attribute1 = request.POST.get('attribute1', "")
        attribute2 = request.POST.get('attribute2', "")
      
        try:
            provenance = Provenance.objects.get(serial=serial)
        except Provenance.DoesNotExist:
            print "bad provenance store_id"
        
        if provenance.node1 == node1 and provenance.node2 == node2 and provenance.attribute1 == attribute1 and provenance.attribute2 == attribute2:
            correct = True
        elif provenance.node2 == node1 and provenance.node1 == node2 and provenance.attribute2 == attribute1 and provenance.attribute1 == attribute2:
            correct = True
        
        if correct:
            message = "Good job, agent!"    
        
        json_data = json.dumps({"correct":correct, "message":message})
    
        return HttpResponse(json_data, mimetype="application/json")
            
            
#    message = -1
#    if request.is_ajax():
#        if request.method == 'POST':
#
#            pebble_id = request.POST.get('pebble_id', "")
#            marble_id = request.POST.get('marble_id', "")
#
#            pebble = get_object_or_404(Pebble, id=int(pebble_id))
#            marble = get_object_or_404(Marble, id=int(marble_id))
#
#            #TODO check if user has rights to delete
#            marble.pebbles.remove(pebble)
#            
#            message = 1
#
#    print message
#    return HttpResponse(message)
    pass

def mop_submit(request):
    pass

    