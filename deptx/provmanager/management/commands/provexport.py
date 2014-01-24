from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from provmanager.provenance import ActionLogProvConverter
from players.models import Player


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-j', '--prov-json',
                    action='store_true',
                    dest='prov-json',
                    default=False,
                    help='Output the PROV-JSON instead of the default PROV-N format'),
        make_option('-b', '--bundled',
                    action='store_true',
                    dest='bundle',
                    default=False,
                    help='Each action has its own bundle'),
        make_option('-s', '--no-spe',
                    action='store_true',
                    dest='no_specialization',
                    default=False,
                    help='Do not generate specialization relations'),
        make_option('-w', '--no-view',
                    action='store_true',
                    dest='no_view',
                    default=False,
                    help='Do not generate provenance for view actions'),
        make_option('-o', '--offset',
                    action='store',
                    type='int',
                    dest='offset',
                    default=0,
                    help='Start from the offset action log'),
        make_option('-l', '--limit',
                    action='store',
                    type='int',
                    dest='limit',
                    default=None,
                    help='Limit the number of action logs to convert'),
        make_option('-i', '--log-ids',
                    action='store',
                    type='string',
                    dest='ids',
                    default=None,
                    help='Only generating provenance for action whose ids are provided (comma separated, no space)'),
    )
    args = '<player_id>'
    help = 'Exporting the provenance for player IDs'

    def handle(self, *args, **options):
        for player_id in args:
            try:
                player = Player.objects.get(pk=int(player_id))
            except Player.DoesNotExist:
                raise CommandError('Player "%s" does not exist' % player_id)

            converter = ActionLogProvConverter(player, options['bundle'], not options['no_specialization'],
                                               not options['no_view'])

            # Start the conversion
            ids = None
            if options['ids']:
                ids = map(int, options['ids'].split(','))
            converter.convert(options['offset'], options['limit'], ids)

            if options['prov-json']:
                self.stdout.write(converter.get_provjson())
            else:
                self.stdout.write(converter.get_provn())
