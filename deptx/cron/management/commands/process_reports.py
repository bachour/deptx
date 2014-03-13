from django.core.management.base import NoArgsCommand

from cron.reportchecker import analyze_reports

class Command(NoArgsCommand):
    help = "Automated Case Report Checker"
    def handle_noargs(self, **options):
        analyze_reports()