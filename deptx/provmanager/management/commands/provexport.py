from django.core.management.base import BaseCommand, CommandError
from provmanager.provenance import export
from players.models import Player


class Command(BaseCommand):
    args = '<player_id>'
    help = 'Exporting the provenance for player IDs'

    def handle(self, *args, **options):
        for player_id in args:
            try:
                player = Player.objects.get(pk=int(player_id))
            except Player.DoesNotExist:
                raise CommandError('Player "%s" does not exist' % player_id)

            g = export(player)

            self.stdout.write('Exporting "%s"' % player_id)
            self.stdout.write(g.get_provn())
