from django.shortcuts import render, render_to_response, redirect

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext

from assets.models import Document, Provenance
from persistence.models import PDBundle

from assets.models import GRAPH_FOLDER, JSON_FOLDER
from deptx.settings import MEDIA_ROOT
from prov.model.graph import prov_to_file
from deptx.helpers import generateUUID
from prov_tests import *

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

def index(request):
    document_list = Document.objects.all()
    provenance_list = Provenance.objects.all()
    pdbundle_list = PDBundle.objects.all()
    
    return render(request, 'provmaker/index.html', {"document_list":document_list, "provenance_list": provenance_list, "pdbundle_list":pdbundle_list},
                  context_instance=RequestContext(request))

def provenance(request, prov_id):
    pdBundle = PDBundle.objects.get(id=prov_id)
    g = pdBundle.get_prov_bundle()
    
    return render_prov(request, g)
    
def example(request, test_id):
    
    test_id = int(test_id)

    if test_id==1:
        g = prov_test1()
    elif test_id==2:
        g = prov_test2()
    elif test_id==3:
        g = prov_test3()
    elif test_id==4:
        g = prov_test4()
    else:
        g = None
    return render_prov(request, g)
    
def render_prov(request, g):
    
    #TODO file is regenerated every time under a different name
    
    fileid = generateUUID()
    imagename = fileid + ".png"
    path = MEDIA_ROOT + "/" + GRAPH_FOLDER
    prov_to_file(g, path + imagename, use_labels=False, show_element_attributes=False, show_relation_attributes=False)
    imageurl = GRAPH_FOLDER + imagename
    
    json_str = g.get_provjson(indent=4)
    
    jsonname = fileid + ".json"
    jsonurl = JSON_FOLDER + jsonname
    with open(MEDIA_ROOT + "/" + JSON_FOLDER + jsonname, "w") as text_file:
        text_file.write(json_str)
    
    return render(request, 'provmaker/provenance.html', {'pdbundle':g, 'json_str':json_str, 'imageurl':imageurl, 'jsonurl':jsonurl},
                  context_instance=RequestContext(request))
