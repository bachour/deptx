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
    )
    args = '<player_id>'
    help = 'Exporting the provenance for player IDs'

    def handle(self, *args, **options):
        for player_id in args:
            try:
                player = Player.objects.get(pk=int(player_id))
            except Player.DoesNotExist:
                raise CommandError('Player "%s" does not exist' % player_id)

            converter = ActionLogProvConverter(player)

            if options['prov-json']:
                self.stdout.write(converter.get_provjson())
            else:
                self.stdout.write(converter.get_provn())