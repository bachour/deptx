from django.core.management.base import NoArgsCommand

from mop.documentcreator import create_documents

class Command(NoArgsCommand):
    help = "Automated Document Creator"
    def handle_noargs(self, **options):
        pass
        create_documents()