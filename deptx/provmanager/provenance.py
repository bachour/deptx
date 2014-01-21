from django.db.models import Q
from django.db.models.fields.related import ForeignKey
from prov.model import ProvBundle
from players.models import Mop
from logger.models import ActionLog


# All the prefixes used in the provenance export
NAMESPACES = {
    'player': 'http://www.cr0n.org/players/',
    'cron': 'http://www.cr0n.org/ns#',
    'server': 'http://www.cr0n.org/server/',
    'act': 'http://www.cr0n.org/ns#act',
    'asset': 'http://www.cr0n.org/ns#asset',
    'log': 'http://www.cr0n.org/log/',
    'b': 'http://www.cr0n.org/bundles/',
    'cronuser': 'http://www.cr0n.org/user/',
    'mopuser': 'http://mofp.net/user/',
    'mop': 'http://mofp.net/ns#',
    'dept': 'http://mofp.net/departments/',
    'form': 'http://mofp.net/forms/',
    'doc': 'http://mofp.net/documents/',
    'foaf': 'http://xmlns.com/foaf/0.1/',  # see http://xmlns.com/foaf/spec/
}


def model_to_dict(instance):
    """Extract not-None fields of a Django object instance into a dictionary
    """
    data = {}
    for field in instance._meta.fields:
        field_value = field.value_from_object(instance)
        if field_value is not None:
            data[field.name] = field.rel.to.objects.get(pk=field_value) if isinstance(field, ForeignKey) else field_value
    return data


def action_log_to_dict(action_log):
    data = model_to_dict(action_log)
    data['action'] = action_log.get_action_display()
    if 'missionState' in data:
        data['missionState'] = action_log.get_missionState_display()
    return data


def convert_action_log(g, element_cache, log):
    data = action_log_to_dict(log)


def export(player):
    element_cache = {}
    g = ProvBundle(namespaces=NAMESPACES)

    # The main player agent
    # TODO: Decide which attributes to include: name, gender, age, town, country, createdAt
    ag_player = g.agent('player:{player_id}'.format(player_id=player.id))
    element_cache[player] = ag_player

    # The Cron specific
    cron = player.cron
    # TODO: Decide which attributes to include: activationCode, activated, email, cancelled, overSixteen, createdAt
    ag_cron = g.agent('cronuser:{cron_id}'.format(cron_id=cron.id))
    element_cache[cron] = ag_cron
    g.specialization(ag_cron, ag_player)

    # The Mop player
    # TODO: Check whether there is only one Mop per Cron
    mop = Mop.objects.get(cron=cron)
    # TODO: Decide which attributes to include: hair, eyes, weight, firstname, dob, lastname, height, gender, active,
    # serial, marital, createdAt
    ag_mop = g.agent('mopuser:{mop_id}'.format(mop_id=mop.id))
    element_cache[mop] = ag_mop
    g.specialization(ag_mop, ag_player)
    g.alternate(ag_mop, ag_cron)

    actions_logs = ActionLog.objects.filter(Q(cron=cron) | Q(mop=mop)).order_by('id')
    for log in actions_logs:
        convert_action_log(g, element_cache, log)
    return g
