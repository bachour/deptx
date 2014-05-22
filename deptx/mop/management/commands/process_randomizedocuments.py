from django.core.management.base import NoArgsCommand

from mop.documentcreator import create_documents, remove_old_documents


class Command(NoArgsCommand):
    help = "Automated Daily Document Creator"
    def handle_noargs(self, **options):
        #remove_old_documents()
        #create_documents()