from django.core.management.base import NoArgsCommand

from mop.mailserver import analyze_mail

class Command(NoArgsCommand):
    help = "Automated Mailserver"
    def handle_noargs(self, **options):
        analyze_mail()