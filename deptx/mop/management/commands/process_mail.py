from django.core.management.base import NoArgsCommand

from mop.mailserver import analyze_sent_mail

class Command(NoArgsCommand):
    help = "Automated Mailserver"
    def handle_noargs(self, **options):
        pass
        analyze_sent_mail()