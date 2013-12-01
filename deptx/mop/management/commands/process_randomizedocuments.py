from django.core.management.base import NoArgsCommand

from mop.documentcreator import create_daily_documents


class Command(NoArgsCommand):
    help = "Automated Daily Document Creator"
    def handle_noargs(self, **options):
        create_daily_documents()