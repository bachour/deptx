from mop.models import RandomizedDocument
from assets.models import MopDocument
from provmanager.views import randomize_document

def create_documents():
    for x in range(0, 5):
        mopDocument = MopDocument.objects.all().order_by('?')[0]
        randomizedDocument = randomize_document(mopDocument)
        print randomizedDocument.serial
    

        
