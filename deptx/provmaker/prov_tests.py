from prov.model import ProvBundle, Namespace, Literal, PROV, XSD, Identifier
from persistence.models import save_bundle

def prov_test1():
    g = ProvBundle()
    
    g.entity('crashed car')
    g.entity('written statement')
    g.entity('call log')
    g.entity('blood report 1')
    g.entity('blood report 2')
    g.entity('blood report 3')
    g.entity('mechanic report')
    g.entity('final report')
        
    g.activity('police interview')
    g.activity('emergency call', '2012-03-31T09:21:00', '2012-04-01T15:21:00')
    g.activity('crash')
    g.activity('investigation')
    g.activity('blood analysis 1')
    g.activity('blood analysis 2')
    g.activity('blood analysis 3')
    g.activity('examination')
    
    g.agent('Henry Driver', {'type': 'Person', 'sex': 'male', 'birthdate': '1960-12-01', 'email': 'derek@example.org'})
    g.agent('Witness')
    g.agent('Paul Smith')
    g.agent('Mechanic')
    g.agent('Dr Stevens')
    g.agent('Lady Di')
    g.agent('Dodi')
    g.agent('Officer Charley')
    g.agent('Officer Junior')
    
    g.wasGeneratedBy('written statement', 'police interview')
    g.wasGeneratedBy('crashed car', 'crash')
    g.wasGeneratedBy('call log', 'emergency call')
    g.wasGeneratedBy('mechanic report', 'examination')
    g.wasGeneratedBy('blood report 1', 'blood analysis 1')
    g.wasGeneratedBy('blood report 2', 'blood analysis 2')
    g.wasGeneratedBy('blood report 3', 'blood analysis 3')
    g.wasGeneratedBy('final report', 'investigation')
  
    g.used('examination', 'crashed car')    
    g.used('investigation', 'mechanic report')
    g.used('investigation', 'blood report 1')
    g.used('investigation', 'blood report 2')
    g.used('investigation', 'blood report 3')
    g.used('investigation', 'call log')
    g.used('investigation', 'written statement')
    g.wasAssociatedWith('examination', 'Mechanic')
    g.wasAssociatedWith('crash', 'Henry Driver')
    g.wasAssociatedWith('crash', 'Lady Di')
    g.wasAssociatedWith('crash', 'Dodi')
    g.wasAssociatedWith('police interview', 'Witness')
    g.wasAssociatedWith('emergency call', 'Paul Smith')
    g.used('blood analysis 1', 'blood sample 1')
    g.used('blood analysis 2', 'blood sample 2')
    g.used('blood analysis 3', 'blood sample 3')
    
    g.wasDerivedFrom('blood sample 1', 'Henry Driver', other_attributes={'type': 'sucking blood'})
    g.wasDerivedFrom('blood sample 2', 'Lady Di')
    g.wasDerivedFrom('blood sample 3', 'Dodi')
    g.wasInformedBy('emergency call', 'crash')
    g.wasInformedBy('police interview', 'crash')
    
    g.wasAssociatedWith('blood analysis 1', 'Dr Stevens')
    g.wasAssociatedWith('blood analysis 2', 'Dr Stevens')
    g.wasAssociatedWith('blood analysis 3', 'Dr Stevens')
    g.wasAssociatedWith('investigation', 'Officer Charley')
    g.wasAssociatedWith('police interview', 'Officer Junior')
    g.actedOnBehalfOf('Officer Junior', 'Officer Charley')

#     print g
#     bundle = save_bundle(g)
#     filename = generateUUID()
#     
#     prov_to_file(g, MEDIA_ROOT + "/" + filename + ".png")
#     print MEDIA_ROOT
    return g

def prov_test2():
    g = ProvBundle()
    
    g.agent('helen_blank', {'prov:label':'Helen Blank', 'image':'http://www.welfareacademy.org/conf/papers/blank.jpg', 'birthdate':'1967-01-23', 'sex':'female', 'height':'168cm', 'eyes':'blue', 'address':'127 Makeup St, 3422 New Burlington, Latveria', 'profession': 'bank robber', 'employer':'Bank of England'})
    g.agent('adele_basson', {'prov:label':'Adele Basson', 'image':'http://www.liveindia.com/missworld/Namibia.jpg', 'birthdate':'1976-11-09', 'sex':'female', 'height':'179cm', 'eyes':'green', 'address':'7 Parliament Road, 4222 Old Burlington, Latveria', 'profession': 'emergency operators', 'employer':'Emergency Services'})
    g.agent('james_bradbury', {'prov:label':'James Bradbury', 'image':'http://d2om8tvz4lgco4.cloudfront.net/archive/x188777883/g12c00000000000000036691c2645c87eb2b64f3a3dddc2a958ba284e63.jpg', 'birthdate':'1921-08-08', 'sex':'male', 'height':'124cm', 'eyes':'brown', 'address':'The cupboard under the stairs, Little Wiggum, Redland', 'profession': 'translator', 'employer':'Ministry of Provenance'})
    g.agent('mop_ai', {'prov:label':'Transcription A.I.', 'image':'http://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/HAL9000.svg/250px-HAL9000.svg.png', 'version': '0.0.1beta'})
        
    g.entity('phone_recording', {'prov:label':'audio recording', 'image':'http://www.opexhosting.co.uk/i/news/126478461033371.jpg', 'type': 'audio', 'file':'something.mp3'})
    g.entity('french_transcript', {'prov:label':'transcript', 'image':'http://www.mcgill.ca/gps/sites/mcgill.ca.gps/files/images/french-sheet-thumb_0.png', 'type':'pdf', 'file':'something.pdf'})
    g.entity('english_transcript', {'prov:label':'transcript', 'image':'http://www.aberystwythpenparcau-communitiesfirst.org.uk/wp-content/uploads/2011/07/Consultation-Guide-English.jpg', 'type':'pdf', 'file':'something_else.pdf'})
    
    g.activity('112_call', other_attributes={'prov:label':'emergency call', 'starttime':'1997-08-31-23:23:12', 'endtime':'1997-08-31-23:27:25' })
    g.activity('transcription', other_attributes={'prov:label':'transcription', 'starttime':'1997-08-31-23:28:14', 'endtime':'1997-08-31-23:31:56'})
    g.activity('translation', other_attributes={'prov:label':'translation', 'starttime':'1997-09-12-10:34:16', 'endtime':'1997-09-12-14:56:09'})
    
    g.wasGeneratedBy('english_transcript', 'translation', other_attributes={'prov:role':'output of'})
    g.used('translation', 'french_transcript', other_attributes={'prov:role':'input for'})
    g.wasAssociatedWith('translation', 'james_bradbury', other_attributes={'prov:role':'translated by'})
    
    g.wasGeneratedBy('french_transcript', 'transcription', other_attributes={'prov:role':'output of'})
    g.used('transcription', 'phone_recording', other_attributes={'prov:role':'input for'})
    g.wasAssociatedWith('transcription', 'mop_ai', other_attributes={'prov:role':'transcribed by'})
    
    g.wasGeneratedBy('phone_recording', '112_call', other_attributes={'prov:role':'output of'})
    g.wasAssociatedWith('112_call', 'helen_blank', other_attributes={'prov:role':'caller'})
    g.wasAssociatedWith('112_call', 'adele_basson', other_attributes={'prov:role':'call handler'})
    
    
    g.wasAttributedTo('english_transcript', 'james_bradbury', other_attributes={'prov:role':'created by'})
    g.wasDerivedFrom('english_transcript', 'french_transcript', other_attributes={'prov:role':'translation of'})
    
    g.wasAttributedTo('french_transcript', 'mop_ai', other_attributes={'prov:role':'transcribed by'})
    g.wasDerivedFrom('french_transcript', 'phone_recording', other_attributes={'prov:role':'transcript of'})
    
    g.wasAttributedTo('phone_recording', 'helen_blank', other_attributes={'prov:role':'caller'})
    g.wasAttributedTo('phone_recording', 'adele_basson', other_attributes={'prov:role':'call handler'})

    return g


def prov_test3():
    g = ProvBundle()

    #    prefix ex <http://example/>
    #    prefix dcterms <http://purl.org/dc/terms/>
    #    prefix foaf <http://xmlns.com/foaf/0.1/>
    ex = Namespace('ex', 'http://example/')  # namespaces do not need to be explicitly added to a document
    g.add_namespace("dcterms", "http://purl.org/dc/terms/")
    g.add_namespace("foaf", "http://xmlns.com/foaf/0.1/")

    #    entity(ex:article, [dcterms:title="Crime rises in cities"])
    g.entity(ex['article'], {'dcterms:title': "Crime rises in cities"})  # first time the ex namespace was used, it is added to the document automatically
    #    entity(ex:articleV1)
    g.entity(ex['articleV1'])
    #    entity(ex:articleV2)
    g.entity(ex['articleV2'])
    #    entity(ex:dataSet1)
    g.entity(ex['dataSet1'])
    #    entity(ex:dataSet2)
    g.entity(ex['dataSet2'])
    #    entity(ex:regionList)
    g.entity(ex['regionList'])
    #    entity(ex:composition)
    g.entity(ex['composition'])
    #    entity(ex:chart1)
    g.entity(ex['chart1'])
    #    entity(ex:chart2)
    g.entity(ex['chart2'])
    #    entity(ex:blogEntry)
    g.entity(ex['blogEntry'])

    #    activity(ex:compile)
    g.activity('ex:compile')  # since ex is registered, it can be used like this
    #    activity(ex:compile2)
    g.activity('ex:compile2')
    #    activity(ex:compose)
    g.activity('ex:compose')
    #    activity(ex:correct, 2012-03-31T09:21:00, 2012-04-01T15:21:00)
    g.activity('ex:correct', '2012-03-31T09:21:00', '2012-04-01T15:21:00')  # date time can be provided as strings
    #    activity(ex:illustrate)
    g.activity('ex:illustrate')

    #    used(ex:compose, ex:dataSet1, -,   [ prov:role = "ex:dataToCompose"])
    g.used('ex:compose', 'ex:dataSet1', other_attributes={'prov:role': "ex:dataToCompose"})
    #    used(ex:compose, ex:regionList, -, [ prov:role = "ex:regionsToAggregateBy"])
    g.used('ex:compose', 'ex:regionList', other_attributes={'prov:role': "ex:regionsToAggregateBy"})
    #    wasGeneratedBy(ex:composition, ex:compose, -)
    g.wasGeneratedBy('ex:composition', 'ex:compose')

    #    used(ex:illustrate, ex:composition, -)
    g.used('ex:illustrate', 'ex:composition')
    #    wasGeneratedBy(ex:chart1, ex:illustrate, -)
    g.wasGeneratedBy('ex:chart1', 'ex:illustrate')

    #    wasGeneratedBy(ex:chart1, ex:compile,  2012-03-02T10:30:00)
    g.wasGeneratedBy('ex:chart1', 'ex:compile', '2012-03-02T10:30:00')
    #    wasGeneratedBy(ex:chart2, ex:compile2, 2012-04-01T15:21:00)
    #
    #
    #    agent(ex:derek, [ prov:type="prov:Person", foaf:givenName = "Derek",
    #           foaf:mbox= "<mailto:derek@example.org>"])
    g.agent('ex:derek', {'prov:type': PROV["Person"], 'foaf:givenName': "Derek", 'foaf:mbox': "mailto:derek@example.org"})
    #    wasAssociatedWith(ex:compose, ex:derek, -)
    g.wasAssociatedWith('ex:compose', 'ex:derek')
    #    wasAssociatedWith(ex:illustrate, ex:derek, -)
    g.wasAssociatedWith('ex:illustrate', 'ex:derek')
    #
    #    agent(ex:chartgen, [ prov:type="prov:Organization",
    #           foaf:name = "Chart Generators Inc"])
    g.agent('ex:chartgen', {'prov:type': PROV["Organization"], 'foaf:name': "Chart Generators Inc"})
    #    actedOnBehalfOf(ex:derek, ex:chartgen, ex:compose)
    g.actedOnBehalfOf('ex:derek', 'ex:chartgen', 'ex:compose')
    #    wasAttributedTo(ex:chart1, ex:derek)
    g.wasAttributedTo('ex:chart1', 'ex:derek')

    #    wasGeneratedBy(ex:dataSet2, ex:correct, -)
    g.wasGeneratedBy('ex:dataSet2', 'ex:correct')
    #    used(ex:correct, ex:dataSet1, -)
    g.used('ex:correct', 'ex:dataSet1')
    #    wasDerivedFrom(ex:dataSet2, ex:dataSet1, [prov:type='prov:Revision'])
    g.wasDerivedFrom('ex:dataSet2', 'ex:dataSet1', other_attributes={'prov:type': PROV['Revision']})
    #    wasDerivedFrom(ex:chart2, ex:dataSet2)
    g.wasDerivedFrom('ex:chart2', 'ex:dataSet2')

    #    wasDerivedFrom(ex:blogEntry, ex:article, [prov:type='prov:Quotation'])
    g.wasDerivedFrom('ex:blogEntry', 'ex:article', other_attributes={'prov:type': PROV['Quotation']})
    #    specializationOf(ex:articleV1, ex:article)
    g.specializationOf('ex:articleV1', 'ex:article')
    #    wasDerivedFrom(ex:articleV1, ex:dataSet1)
    g.wasDerivedFrom('ex:articleV1', 'ex:dataSet1')

    #    specializationOf(ex:articleV2, ex:article)
    g.specializationOf('ex:articleV2', 'ex:article')
    #    wasDerivedFrom(ex:articleV2, ex:dataSet2)
    g.wasDerivedFrom('ex:articleV2', 'ex:dataSet2')

    #    alternateOf(ex:articleV2, ex:articleV1)
    g.alternateOf('ex:articleV2', 'ex:articleV1')

    # endDocument
    return g

def prov_test4():
    g = ProvBundle()
    
#     g.agent('a1')
#     g.agent('a2')
#     g.agent('b1')
#     g.agent('b2')
#     g.agent('c1')
#     g.agent('c2')
#     g.agent('d1')
#     g.agent('d2')
#     g.agent('e1')
#     g.agent('e2')
#     g.agent('f1')
#     g.agent('f2')
#     g.agent('g1')
#     g.agent('g2')
#     g.agent('h1')
#     g.agent('h2')
#     g.agent('i1')
#     g.agent('i2')
#     g.agent('j1')
#     g.agent('j2')
#     g.agent('k1')
#     g.agent('k2')
#     g.agent('l1')
#     g.agent('l2')
#     g.agent('m1')
#     g.agent('m2')
#     g.agent('n1')
#     g.agent('n2')
        
    g.wasDerivedFrom("a1", "a2", other_attributes={'prov:role': 'my role'})
    g.alternateOf("b1", "b2", other_attributes={'prov:role': 'my role'})
    g.specializationOf("c1", "c2", other_attributes={'prov:role': 'my role'})
    g.hadMember("d1", "d2", other_attributes={'prov:role': 'my role'})
    g.wasAttributedTo("e1", "e2", other_attributes={'prov:role': 'my role'})
    g.wasInfluencedBy("f1", "f2", other_attributes={'prov:role': 'my role'})
    g.wasGeneratedBy("g1", "g2", other_attributes={'prov:role': 'my role'})
    g.wasInvalidatedBy("h1", "h2", other_attributes={'prov:role': 'my role'})
    g.used("i1", "i2", other_attributes={'prov:role': 'my role'})
    g.wasStartedBy("j1", "j2", other_attributes={'prov:role': 'my role'})
    g.wasEndedBy("k1", "k2", other_attributes={'prov:role': 'my role'})
    g.wasAssociatedWith("l1", "l2", other_attributes={'prov:role': 'my role'})
    g.wasInformedBy("m1", "m2", other_attributes={'prov:role': 'my role'})
    g.actedOnBehalfOf("n1", "n2", other_attributes={'prov:role': 'my role'})
    
                                                    
    return g

