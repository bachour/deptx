from django.db.models import Q
from django.db.models.fields.related import ForeignKey
from prov.model import ProvBundle
from mop.models import Mail
from logger.models import ActionLog


# All the prefixes used in the provenance export
from players.models import Mop

NAMESPACES = {
    'user': 'http://www.cr0n.org/users/',
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
    'mopmail': 'http://mofp.net/mail/',
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


def _create_action_mop_view_function(view):
    def action_mop_view_function(self, bundle, log):
        self._create_mop_view_action(bundle, log, view)

    action_mop_view_function.__name__ = 'action_mop_view_' + view
    return action_mop_view_function


def _create_action_cron_view_function(view):
    def action_cron_view_function(self, bundle, log):
        self._create_cron_view_action(bundle, log, view)

    action_cron_view_function.__name__ = 'action_cron_view_' + view
    return action_cron_view_function


class ActionLogProvConverter():
    def __init__(self, user,
                 generating_bundle=True,
                 generating_specialization=True,
                 including_view_actions=True):
        self.cache = {}
        self.generating_bundle = generating_bundle
        self.including_view_actions = including_view_actions
        self.generating_cron_specialization = generating_specialization
        self.generating_mop_specialization = generating_specialization

        self.prov = ProvBundle(namespaces=NAMESPACES)
        self.user = user
        self.cron = user.cron
        self.mop = Mop.objects.get(cron=user.cron)

        g = self.prov

        # The main player agent
        # TODO: Decide which attributes to include: name, gender, age, town, country, createdAt
        self.ag_player = g.agent('user:{user_id}'.format(user_id=user.id))

        # The Cron specific
        # TODO: Decide which attributes to include: activationCode, activated, email, cancelled, overSixteen, createdAt
        self.ag_cron = g.agent('cronuser:{cron_id}'.format(cron_id=self.cron.id))
        g.specialization(self.ag_cron, self.ag_player)

        # The Mop player
        # TODO: Check whether there is only one Mop per Cron
        # TODO: Decide which attributes to include: hair, eyes, weight, firstname, dob, lastname, height, gender, active,
        # serial, marital, createdAt
        self.ag_mop = g.agent('mopuser:{mop_id}'.format(mop_id=self.mop.id))
        g.specialization(self.ag_mop, self.ag_player)
        g.alternate(self.ag_mop, self.ag_cron)

        self.ag_cron_current = self.ag_cron
        self.ag_mop_current = self.ag_mop

    def convert(self, offset=0, limit=None, ids=None):
        actions_logs = ActionLog.objects.filter(Q(cron=self.cron) | Q(mop=self.mop)).order_by('id')
        if ids:
            actions_logs = actions_logs.filter(id__in=ids)
        if offset or limit:
            actions_logs = actions_logs[offset:] if limit is None else actions_logs[offset:limit]
        for log in actions_logs:
            self._convert_action_log(log)

    def get_provn(self):
        return self.prov.get_provn()

    def get_provjson(self):
        return self.prov.get_provjson()

    def _convert_action_log(self, log):
        if log.action in ActionLogProvConverter._converters:
            bundle = self.prov.bundle('b:{user_id}/{log_id}'.format(user_id=self.user.id, log_id=log.id))\
                if self.generating_bundle else self.prov

            # TODO Surround by try/except block to fail gracefully should there is any exception during conversion
            self._converters[log.action](self, bundle, log)
            if self.generating_bundle:
                if bundle._records:
                    # Cache the bundle for this action log (mainly for debugging)
                    self.cache[log.id] = bundle
                else:
                    # Remove the empty bundle
                    # TODO Remove the hack below
                    self.prov._records.remove(bundle)
                    del self.prov._bundles[bundle.get_identifier()]
        else:
            # TODO: Emit warnings for inconvertible logs
            pass

    def _create_new_cron_entity(self, bundle, log, activity=None, cron_attrs=None):
        ag_cron_new = bundle.agent('cronuser:{cron_id}/{log_id}'.format(cron_id=self.cron.id, log_id=log.id),
                                   cron_attrs)
        if cron_attrs:
            # New attribute(s), this is a revision of the current cron
            bundle.wasRevisionOf(ag_cron_new, self.ag_cron_current)
        else:
            # No new attribute, this is an alternate of the current cron
            bundle.alternateOf(ag_cron_new, self.ag_cron_current)
        if self.generating_cron_specialization:
            bundle.specialization(ag_cron_new, self.ag_cron)
        if activity:
            bundle.wasGeneratedBy(ag_cron_new, activity)
        self.ag_cron_current = ag_cron_new
        return ag_cron_new

    def _create_cron_activity(self, bundle, activity, cron, log, act_attrs=None, cron_attrs=None):
        act_id = 'cronact:{activity}/{cron_id}/{log_id}'.format(activity=activity, cron_id=cron.id, log_id=log.id)
        act = bundle.activity(act_id, log.createdAt, log.createdAt, act_attrs)
        bundle.wasAssociatedWith(act, self.ag_cron_current)
        self._create_new_cron_entity(bundle, log, act, cron_attrs)
        return act

    def _create_cron_view_action(self, bundle, log, view):
        if self.including_view_actions:
            g = bundle
            act = g.activity('cronact:view_{view}/{log_id}'.format(view=view, log_id=log.id),
                             log.createdAt, log.createdAt,
                             {'cron:action_log_id': log.id})
            g.wasAssociatedWith(act, self.ag_cron_current)

    def action_cron_created(self, bundle, log):
        g = bundle
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

    def action_cron_activated(self, bundle, log):
        g = bundle
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

    def action_cron_login(self, bundle, log):
        g = bundle
        cron = log.cron
        act = g.activity('cronact:login/{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id),
                         log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_player)

        ag_cron_logged_in = g.agent('cronuser:{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id))
        g.alternate(ag_cron_logged_in, self.ag_cron_current)
        if self.generating_cron_specialization:
            g.specialization(ag_cron_logged_in, self.ag_cron)
        g.wasGeneratedBy(ag_cron_logged_in, act)
        self.ag_cron_current = ag_cron_logged_in

    def create_mission_action(self, bundle, action, log):
        g = bundle
        mission = log.mission
        e_mission = g.entity('mission:{mission_id}'.format(mission_id=mission.id),
                             {'cron:mission': mission.name})
        e_mission_part = g.entity(
            'mission:{mission_id}/{action}'.format(mission_id=mission.id, action=action)
        )
        g.hadMember(e_mission, e_mission_part)
        act = g.activity(
            'cronact:view_mission_{action}/{mission_id}/{log_id}'.format(mission_id=mission.id,
                                                                         action=action, log_id=log.id),
            log.createdAt, None,
            {'cron:action_log_id': log.id}
        )
        g.wasAssociatedWith(act, self.ag_cron_current)
        g.used(act, e_mission_part)
        ag_cron_new = self._create_new_cron_entity(
            g, log, act,
            {'cron:mission': 'mission:{mission_id}'.format(mission_id=mission.id),
             'cron:missionState': log.get_missionState_display()}
        )
        g.wasDerivedFrom(ag_cron_new, e_mission_part)

    def action_cron_view_mission_intro(self, bundle, log):
        self.create_mission_action(bundle, 'intro', log)

    def action_cron_view_mission_briefing(self, bundle, log):
        self.create_mission_action(bundle, 'briefing', log)

    def action_cron_view_mission_debriefing(self, bundle, log):
        self.create_mission_action(bundle, 'debriefing', log)

    def action_cron_view_mission_outro(self, bundle, log):
        self.create_mission_action(bundle, 'outro', log)

    def action_cron_view_fluff(self, bundle, log):
        self._create_cron_activity(bundle, 'view_fluff', log.cron, log, {'cron:fluff': log.fluff})

    def _create_new_mop_entity(self, bundle, log, activity=None, mop_attrs=None):
        ag_mop_new = bundle.agent('mopuser:{mop_id}/{log_id}'.format(mop_id=self.mop.id, log_id=log.id), mop_attrs)
        if mop_attrs:
            # New attribute(s), this is a revision of the current mop
            bundle.wasRevisionOf(ag_mop_new, self.ag_mop_current)
        else:
            # No new attribute, this is an alternate of the current mop
            bundle.alternateOf(ag_mop_new, self.ag_mop_current)
        if self.generating_mop_specialization:
            bundle.specialization(ag_mop_new, self.ag_mop)
        if activity:
            bundle.wasGeneratedBy(ag_mop_new, activity)
        self.ag_mop_current = ag_mop_new
        return ag_mop_new

    def _create_mop_activity(self, bundle, log, activity, act_attrs=None, mop_attrs=None):
        mop = log.mop
        act_id = 'mopact:{activity}/{mop_id}/{log_id}'.format(activity=activity, mop_id=mop.id, log_id=log.id)
        act = bundle.activity(act_id, log.createdAt, log.createdAt, act_attrs)
        bundle.wasAssociatedWith(act, self.ag_mop_current)
        self._create_new_mop_entity(bundle, log, act, mop_attrs)
        return act

    def _create_mop_view_action(self, bundle, log, view):
        if self.including_view_actions:
            g = bundle
            act = g.activity('mopact:view_{view}/{log_id}'.format(view=view, log_id=log.id),
                             log.createdAt, log.createdAt,
                             {'cron:action_log_id': log.id})
            g.wasAssociatedWith(act, self.ag_mop_current)

    def action_mop_created(self, bundle, log):
        g = bundle
        mop = log.mop
        act = g.activity('mopact:registration/{mop_id}'.format(mop_id=mop.id), log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        g.wasGeneratedBy(self.ag_mop, act)
        g.wasAssociatedWith(act, self.ag_cron_current)
        g.agent('app:mop')
        g.wasAssociatedWith(act, 'app:mop')

        cron = log.cron
        ag_cron_new = g.agent('cronuser:{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id))
        # TODO Describe cron after creating mop
        if self.generating_cron_specialization:
            g.specialization(ag_cron_new, self.ag_cron)
        g.wasGeneratedBy(ag_cron_new, act)
        g.wasRevisionOf(ag_cron_new, self.ag_cron_current)

    def action_mop_login(self, bundle, log):
        g = bundle
        mop = log.mop
        act = g.activity('mopact:login/{mop_id}/{log_id}'.format(mop_id=mop.id, log_id=log.id),
                         log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_player)
        self._create_new_mop_entity(g, log, act)

    def action_mop_receive_mail_tutorial(self, bundle, log):
        self._create_mop_activity(bundle, log, 'receive_mail_tutorial')

    def action_mop_tutorial_progress(self, bundle, log):
        self._create_mop_activity(bundle, log, 'progress_tutorial',
                                  mop_attrs={'cron:tutorialProgress': log.tutorialProgress})

    def _create_form_blank_entity(self, bundle, form_blank, attrs=None):
        return bundle.entity('form:{form_serial}'.format(form_serial=form_blank.serial), attrs)

    def action_mop_form_sign(self, bundle, log):
        mop = log.mop
        form_signed = log.requisitionInstance
        form_blank = form_signed.blank.requisition
        # TODO: Create a new mop or not? Probably not since the mop entity does not change after signing the form
        e_form_blank = self._create_form_blank_entity(bundle, form_blank)
        act = bundle.activity('mopact:form/sign/{mop_id}/{instance_id}'.format(mop_id=mop.id,
                                                                               instance_id=form_signed.id),
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        bundle.used(act, e_form_blank)
        bundle.wasAssociatedWith(act, self.ag_mop_current)
        e_form_signed = bundle.entity(
            'form:{form_serial}/{instance_serial}'.format(form_serial=form_blank.serial,
                                                          instance_serial=form_signed.serial),
            {'mop:timestamp': form_signed.createdAt,
             'mop:data': form_signed.data}
        )
        bundle.wasGeneratedBy(e_form_signed, act)
        bundle.wasDerivedFrom(e_form_signed, e_form_blank, activity=act)

    def _create_mail_entity(self, bundle, mail, attrs=None):
        return bundle.entity(
            'mopmail:{unit}/{mop_id}/{mail_id}'.format(mop_id=mail.mop.id, mail_id=mail.id, unit=mail.unit.serial),
            attrs
        )

    def action_mop_mail_compose_with_form(self, bundle, log):
        # No need to log this action as there is no mail reference to describe the provenance!
        pass

    def action_mop_mail_send(self, bundle, log):
        mop = log.mop
        mail = log.mail

        # The data accompany with the mail
        e_data = None
        if mail.subject == Mail.SUBJECT_REQUEST_FORM:
            form_signed = mail.requisitionInstance
            form_blank = form_signed.blank.requisition
            e_data = bundle.entity(
                'form:{form_serial}/{instance_serial}'.format(form_serial=form_blank.serial,
                                                              instance_serial=form_signed.serial)
            )
        else:
            # TODO Generate the data entity for other types of attachments
            pass

        act = bundle.activity('mopact:mail/send/{mop_id}/{mail_id}'.format(mop_id=mop.id, mail_id=mail.id),
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        if e_data:
            bundle.used(act, e_data)
        bundle.wasAssociatedWith(act, self.ag_mop_current)
        e_mail = self._create_mail_entity(bundle, mail)
        # TODO: Create a new mop or not? Probably not since the mop entity does not change after sending the mail
        bundle.wasGeneratedBy(e_mail, act)
        if e_data:
            bundle.wasDerivedFrom(e_mail, e_data)

    def action_mop_receive_mail_form(self, bundle, log):
        mop = log.mop
        mail = log.mail
        previous_mail = mail.replyTo
        mop_attrs = {}

        # The data accompany with the mail
        if previous_mail:
            e_previous_mail = self._create_mail_entity(bundle, previous_mail)

        if mail.subject == Mail.SUBJECT_RECEIVE_FORM:
            form_blank = mail.requisitionBlank.requisition
            e_form = self._create_form_blank_entity(bundle, form_blank)
            mop_attrs['mop:forms'] = e_form.get_identifier()
        elif mail.subject == Mail.SUBJECT_REPORT_EVALUATION:
            # TODO: Record change of trust value here
            pass
        else:
            # TODO Check if there is any other subject that falls into this action
            pass

        act = bundle.activity('mopact:mail/receive/{mop_id}/{mail_id}'.format(mop_id=mop.id, mail_id=mail.id),
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        if previous_mail:
            bundle.used(act, e_previous_mail)
        bundle.wasAssociatedWith(act, self.ag_mop_current)
        e_mail = self._create_mail_entity(bundle, mail, {'mop:mail_subject': mail.get_subject_display()})

        bundle.wasGeneratedBy(e_mail, act)
        if previous_mail:
            bundle.wasDerivedFrom(e_mail, e_previous_mail)

        self._create_new_mop_entity(bundle, log, act, mop_attrs)

    def action_mop_view_mail(self, bundle, log):
        mop = log.mop
        mail = log.mail

        if mail is None:
            # The reference to the mail was not recorded, nothing to do
            return

        e_mail = self._create_mail_entity(bundle, mail)

        act = bundle.activity('mopact:mail/view/{mop_id}/{mail_id}'.format(mop_id=mop.id, mail_id=mail.id),
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        bundle.used(act, e_mail)
        bundle.wasAssociatedWith(act, self.ag_mop_current)

        self._create_new_mop_entity(bundle, log, act, {'mop:mails_read': e_mail.get_identifier()})

    _converters = {
        ActionLog.ACTION_CRON_CREATED:                  action_cron_created,
        ActionLog.ACTION_CRON_VIEW_INDEX:               _create_action_cron_view_function('index'),
        ActionLog.ACTION_CRON_VIEW_PROFILE:             _create_action_cron_view_function('profile'),
        ActionLog.ACTION_CRON_VIEW_ARCHIVE:             _create_action_cron_view_function('archive'),
        ActionLog.ACTION_CRON_VIEW_STUDY:               _create_action_cron_view_function('study'),
        ActionLog.ACTION_CRON_VIEW_MESSAGES:            _create_action_cron_view_function('messages'),
        ActionLog.ACTION_CRON_VIEW_MESSAGES_COMPOSE:    _create_action_cron_view_function('messages_compose'),
        ActionLog.ACTION_CRON_ACTIVATED:                action_cron_activated,
        ActionLog.ACTION_CRON_LOGIN:                    action_cron_login,
        ActionLog.ACTION_CRON_VIEW_MISSION_INTRO:       action_cron_view_mission_intro,
        ActionLog.ACTION_CRON_VIEW_MISSION_BRIEFING:    action_cron_view_mission_briefing,
        ActionLog.ACTION_CRON_VIEW_MISSION_DEBRIEFING:  action_cron_view_mission_debriefing,
        ActionLog.ACTION_CRON_VIEW_MISSION_OUTRO:       action_cron_view_mission_outro,
        ActionLog.ACTION_CRON_VIEW_FLUFF:               action_cron_view_fluff,

        ActionLog.ACTION_MOP_CREATED:                   action_mop_created,
        ActionLog.ACTION_MOP_LOGIN:                     action_mop_login,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_TUTORIAL:     action_mop_receive_mail_tutorial,
        ActionLog.ACTION_MOP_TUTORIAL_PROGRESS:         action_mop_tutorial_progress,
        ActionLog.ACTION_MOP_VIEW_INDEX:                _create_action_mop_view_function('index'),
        ActionLog.ACTION_MOP_VIEW_INBOX:                _create_action_mop_view_function('inbox'),
        ActionLog.ACTION_MOP_VIEW_OUTBOX:               _create_action_mop_view_function('outbox'),
        ActionLog.ACTION_MOP_VIEW_FORMS_BLANKS:         _create_action_mop_view_function('forms_blank'),
        ActionLog.ACTION_MOP_VIEW_FORMS_SIGNED:         _create_action_mop_view_function('forms_signed'),
        ActionLog.ACTION_MOP_VIEW_DOCUMENTS_POOL:       _create_action_mop_view_function('documents_pool'),
        ActionLog.ACTION_MOP_VIEW_GUIDEBOOK:            _create_action_mop_view_function('guidebook'),
        ActionLog.ACTION_MOP_FORM_SIGN:                 action_mop_form_sign,
        # ActionLog.ACTION_MOP_MAIL_COMPOSE_WITH_FORM:    action_mop_mail_compose_with_form,
        ActionLog.ACTION_MOP_MAIL_SEND:                 action_mop_mail_send,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_FORM:         action_mop_receive_mail_form,
        ActionLog.ACTION_MOP_VIEW_MAIL:                 action_mop_view_mail,
    }


