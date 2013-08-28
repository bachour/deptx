from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from provmanager.wrapper import Api
from provmanager.models import Provenance
from prov.model import ProvBundle

from deptx.api import api_location, api_username, api_key

import json

api = Api(api_location=api_location, api_username=api_username, api_key=api_key)


    
def index(request):
    provenance_list = Provenance.objects.all()
    
    return render(request, 'provmanager/index.html', {'provenance_list':provenance_list})

def view(request, store_id):
    provenance = Provenance.objects.get(store_id=store_id)
    bundle = api.get_document(provenance.store_id)
    svg = getProvSvg(provenance)
    xml = api.get_document(provenance.store_id, format="xml")
    json_str = getProvJson(provenance)

    return render(request, 'provmanager/view.html', {'provenance': provenance, 'bundle':bundle, 'json':json_str, 'svg':svg, 'xml':xml})

def create(request):
    name = "random name"
    bundle = ProvBundle()
    bundle.entity('crashed_car')
    store_id = api.submit_document(bundle, name, public=False)
    
    provenance = Provenance(store_id=store_id, name=name)
    provenance.save()
    return HttpResponseRedirect(reverse('provmanager_index'))

def getProvJson(provenance):
    json_str = api.get_document(provenance.store_id, format="json")
    parsed = json.loads(json_str)
    return json.dumps(parsed, indent=4, sort_keys=True)

def getProvSvg(provenance):
    svg = api.get_document(provenance.store_id, format="svg")
    return svg
    