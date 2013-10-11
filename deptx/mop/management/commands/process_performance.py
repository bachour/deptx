from django.core.management.base import NoArgsCommand

from mop.performer import analyze_performance

class Command(NoArgsCommand):
    help = "Automated Performance Evaluator"
    def handle_noargs(self, **options):
        analyze_performance()