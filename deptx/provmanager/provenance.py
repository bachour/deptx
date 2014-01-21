from django.db.models import Q
from django.db.models.fields.related import ForeignKey
from prov.model import ProvBundle
from players.models import Mop
from logger.models import ActionLog


# All the prefixes used in the provenance export
NAMESPACES = {
    'player': 'http://www.cr0n.org/players/',
    'cron': 'http://www.cr0n.org/ns#',
    'app': 'http://www.cr0n.org/app/',
    'cronact': 'http://www.cr0n.org/activity/',
    'mission': 'http://www.cr0n.org/mission/',
    'asset': 'http://www.cr0n.org/ns#asset',
    'log': 'http://www.cr0n.org/log/',
    'b': 'http://www.cr0n.org/bundles/',
    'cronuser': 'http://www.cr0n.org/user/',
    'mopuser': 'http://mofp.net/user/',
    'mopact': 'http://mofp.net/activity/',
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
            data[field.name] = field.rel.to.objects.get(pk=field_value) if isinstance(field, ForeignKey)\
                else field_value
    return data


def action_log_to_dict(action_log):
    data = model_to_dict(action_log)
    data['action_label'] = action_log.get_action_display()
    if 'missionState' in data:
        data['missionStateLabel'] = action_log.get_missionState_display()
    return data


class ActionLogProvConverter():
    def __init__(self, player):
        self.player = player

        self.prov = ProvBundle(namespaces=NAMESPACES)
        g = self.prov

        # The main player agent
        # TODO: Decide which attributes to include: name, gender, age, town, country, createdAt
        self.ag_player = g.agent('player:{player_id}'.format(player_id=player.id))

        # The Cron specific
        self.cron = player.cron
        # TODO: Decide which attributes to include: activationCode, activated, email, cancelled, overSixteen, createdAt
        self.ag_cron = g.agent('cronuser:{cron_id}'.format(cron_id=self.cron.id))
        g.specialization(self.ag_cron, self.ag_player)

        # The Mop player
        # TODO: Check whether there is only one Mop per Cron
        self.mop = Mop.objects.get(cron=self.cron)
        # TODO: Decide which attributes to include: hair, eyes, weight, firstname, dob, lastname, height, gender, active,
        # serial, marital, createdAt
        self.ag_mop = g.agent('mopuser:{mop_id}'.format(mop_id=self.mop.id))
        g.specialization(self.ag_mop, self.ag_player)
        g.alternate(self.ag_mop, self.ag_cron)

        self.ag_cron_current = self.ag_cron
        self.ag_mop_current = self.ag_mop

        actions_logs = ActionLog.objects.filter(Q(cron=self.cron) | Q(mop=self.mop)).order_by('id')
        for log in actions_logs:
            self.convert_action_log(log)

    def convert_action_log(self, log):
        if log.action in ActionLogProvConverter._converters:
            # TODO Surround by try/except block to fail gracefully should there is any exception during conversion
            self._converters[log.action](self, log)
        else:
            # TODO: Emit warnings for inconvertible logs
            pass

    def get_provn(self):
        return self.prov.get_provn()

    def get_provjson(self):
        return self.prov.get_provjson()

    def action_cron_created(self, log):
        g = self.prov
        cron = log.cron

        act = g.activity('cronact:registration/{cron_id}'.format(cron_id=cron.id), log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        ag_cron_inactive = g.agent('cronuser:{cron_id}/inactive'.format(cron_id=cron.id))
        self.ag_cron_current = ag_cron_inactive
        g.specialization(ag_cron_inactive, self.ag_cron)
        g.wasGeneratedBy(ag_cron_inactive, act)
        g.wasAssociatedWith(act, self.ag_player)
        g.agent('app:cron')
        g.wasAssociatedWith(act, 'app:cron')

    def action_cron_view_study(self, log):
        g = self.prov
        act = g.activity('cronact:view_study/{log_id}'.format(log_id=log.id), log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_cron_current)

    def action_cron_activated(self, log):
        g = self.prov
        cron = log.cron
        act = g.activity('cronact:activation/{cron_id}'.format(cron_id=cron.id), log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_player)
        g.used(act, self.ag_cron_current)
        ag_cron_active = g.agent('cronuser:{cron_id}/active'.format(cron_id=cron.id))
        g.wasGeneratedBy(ag_cron_active, act)
        g.wasRevisionOf(ag_cron_active, self.ag_cron_current, time=log.createdAt)
        g.specialization(ag_cron_active, self.ag_cron)
        self.ag_cron_current = ag_cron_active

    def action_cron_login(self, log):
        g = self.prov
        cron = log.cron
        act = g.activity('cronact:login/{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id),
                         log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_player)
        ag_cron_logged_in = g.agent('cronuser:{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id))
        g.alternate(ag_cron_logged_in, self.ag_cron_current)
        g.specialization(ag_cron_logged_in, self.ag_cron)
        g.wasGeneratedBy(ag_cron_logged_in, act)
        self.ag_cron_current = ag_cron_logged_in

    def action_cron_view_index(self, log):
        g = self.prov
        act = g.activity('cronact:view_index/{log_id}'.format(log_id=log.id), log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_cron_current)

    def action_cron_view_mission_intro(self, log):
        g = self.prov
        cron = log.cron
        mission = log.mission
        e_mission_intro = g.entity('mission:{mission_id}/intro'.format(mission_id=mission.id))
        act = g.activity('cronact:view_mission_intro/{mission_id}/{log_id}'.format(mission_id=mission.id, log_id=log.id),
                         log.createdAt, None,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_cron_current)
        g.used(act, e_mission_intro)
        ag_cron_new = g.agent('cronuser:{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id),
                              {'cron:mission': 'mission:{mission_id}'.format(mission_id=mission.id),
                               'cron:missionState': log.get_missionState_display()})
        g.specialization(ag_cron_new, self.ag_cron)
        g.wasGeneratedBy(ag_cron_new, act)
        g.wasRevisionOf(ag_cron_new, self.ag_cron_current)
        g.wasDerivedFrom(ag_cron_new, e_mission_intro)
        self.ag_cron_current = ag_cron_new

    def action_cron_view_mission_briefing(self, log):
        g = self.prov
        cron = log.cron
        mission = log.mission
        e_mission_briefing = g.entity('mission:{mission_id}/briefing'.format(mission_id=mission.id))
        act = g.activity('cronact:view_mission_briefing/{mission_id}/{log_id}'.format(mission_id=mission.id, log_id=log.id),
                         log.createdAt, None,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_cron_current)
        g.used(act, e_mission_briefing)
        ag_cron_new = g.agent('cronuser:{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id),
                              {'cron:mission': 'mission:{mission_id}'.format(mission_id=mission.id),
                               'cron:missionState': log.get_missionState_display()})
        g.specialization(ag_cron_new, self.ag_cron)
        g.wasGeneratedBy(ag_cron_new, act)
        g.wasRevisionOf(ag_cron_new, self.ag_cron_current)
        g.wasDerivedFrom(ag_cron_new, e_mission_briefing)
        self.ag_cron_current = ag_cron_new

    def action_mop_created(self, log):
        g = self.prov
        mop = log.mop

        act = g.activity('mopact:registration/{mop_id}'.format(mop_id=mop.id), log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        ag_mop_inactive = g.agent('mopuser:{mop_id}/inactive'.format(mop_id=mop.id))
        self.ag_mop_current = ag_mop_inactive
        g.specialization(ag_mop_inactive, self.ag_mop)
        g.wasGeneratedBy(ag_mop_inactive, act)
        g.wasAssociatedWith(act, self.ag_cron_current)
        g.agent('app:mop')
        g.wasAssociatedWith(act, 'app:mop')

        cron = log.cron
        ag_cron_new = g.agent('cronuser:{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id))
        # TODO Describe cron after creating mop
        g.specialization(ag_cron_new, self.ag_cron)
        g.wasGeneratedBy(ag_cron_new, act)
        g.wasRevisionOf(ag_cron_new, self.ag_cron_current)

    _converters = {
        ActionLog.ACTION_CRON_CREATED:                  action_cron_created,
        ActionLog.ACTION_CRON_VIEW_STUDY:               action_cron_view_study,
        ActionLog.ACTION_CRON_ACTIVATED:                action_cron_activated,
        ActionLog.ACTION_CRON_LOGIN:                    action_cron_login,
        ActionLog.ACTION_CRON_VIEW_INDEX:               action_cron_view_index,
        ActionLog.ACTION_CRON_VIEW_MISSION_INTRO:       action_cron_view_mission_intro,
        ActionLog.ACTION_CRON_VIEW_MISSION_BRIEFING:    action_cron_view_mission_briefing,

        ActionLog.ACTION_MOP_CREATED:                   action_mop_created,
    }