from uuid import uuid4
from django.db.models import Q
from django.db.models.fields.related import ForeignKey
from prov.model import ProvBundle, PROV
from players.models import Cron, Mop
from mop.models import Mail, PerformanceInstance
from logger.models import ActionLog


# All the prefixes used in the provenance export

NAMESPACES = {
    'user': 'http://www.cr0n.org/users/',
    'cron': 'http://www.cr0n.org/ns#',
    'app': 'http://www.cr0n.org/app/',
    'cronact': 'http://www.cr0n.org/activity/',
    'mission': 'http://www.cr0n.org/mission/',
    'asset': 'http://www.cr0n.org/asset/',
    'case': 'http://www.cr0n.org/case/',
    'crondoc': 'http://www.cr0n.org/document/',
    'log': 'http://www.cr0n.org/log/',
    'cronuser': 'http://www.cr0n.org/user/',
    'mopuser': 'http://mofp.net/user/',
    'mopact': 'http://mofp.net/activity/',
    'mopmail': 'http://mofp.net/mail/',
    'mop': 'http://mofp.net/ns#',
    'dept': 'http://mofp.net/department/',
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
        return self._create_cron_view_action(bundle, log, view)

    action_cron_view_function.__name__ = 'action_cron_view_' + view
    return action_cron_view_function


class ActionLogProvConverter():
    VIEW_ACTIONS = {
        ActionLog.ACTION_CRON_VIEW_INDEX,
        ActionLog.ACTION_CRON_VIEW_PROFILE,
        ActionLog.ACTION_CRON_VIEW_ARCHIVE,
        ActionLog.ACTION_CRON_VIEW_MESSAGES,
        ActionLog.ACTION_CRON_VIEW_MESSAGES_COMPOSE,
        ActionLog.ACTION_MOP_VIEW_INDEX,
        ActionLog.ACTION_MOP_VIEW_GUIDEBOOK,
        ActionLog.ACTION_MOP_VIEW_PERFORMANCE,
        ActionLog.ACTION_MOP_VIEW_COMPOSE,
        ActionLog.ACTION_MOP_VIEW_EDIT,
        ActionLog.ACTION_MOP_VIEW_INBOX,
        ActionLog.ACTION_MOP_VIEW_OUTBOX,
        ActionLog.ACTION_MOP_VIEW_DRAFT,
        ActionLog.ACTION_MOP_VIEW_TRASH,
        ActionLog.ACTION_MOP_VIEW_MAIL,
        ActionLog.ACTION_MOP_VIEW_FORMS_BLANKS,
        ActionLog.ACTION_MOP_VIEW_FORMS_FILL,
        ActionLog.ACTION_MOP_VIEW_FORMS_SIGNED,
        ActionLog.ACTION_MOP_VIEW_FORMS_ARCHIVE,
        ActionLog.ACTION_MOP_VIEW_DOCUMENTS_POOL,
        ActionLog.ACTION_MOP_VIEW_DOCUMENTS_DRAWER,
        ActionLog.ACTION_MOP_VIEW_DOCUMENTS_ARCHIVE,
    }
    TRUST_MODIFYING_ACTIONS = {
        ActionLog.ACTION_MOP_RECEIVE_MAIL_ERROR,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_DOCUMENT,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_REPORT,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_PERFORMANCE,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_MANUAL
    }

    def __init__(self, user,
                 generating_bundle=True, bundle_attribution=False,
                 generating_specialization=False,
                 including_view_actions=False,):
        self.session_id = str(uuid4())
        self.cache = {}
        self.general_entities = {}
        self.trust = 0  # The current trust level of mop
        self.trust_total = 0
        self.generating_bundle = generating_bundle
        self.bundle_attribution = bundle_attribution
        self.including_view_actions = including_view_actions
        self.generating_cron_specialization = generating_specialization
        self.generating_mop_specialization = generating_specialization

        self.prov = ProvBundle(namespaces=NAMESPACES)
        if self.generating_bundle:
            bundle_ns_uri = 'http://www.cr0n.org/provexport/{uuid}/'.format(uuid=self.session_id)
            self.prov.add_namespace('b', bundle_ns_uri)
            self.prov.agent('b:script')

        self.user = user
        try:
            self.cron = user.cron
            self.mop = Mop.objects.get(cron=self.cron)
        except Cron.DoesNotExist:
            self.mop = user.mop
            self.cron = self.mop.cron

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
        # TODO: Decide which attributes to include: hair, eyes, weight, firstname, dob, lastname, height, gender,
        # active, serial, marital, createdAt
        self.ag_mop = g.agent('mopuser:{mop_id}'.format(mop_id=self.mop.id))
        g.specialization(self.ag_mop, self.ag_player)
        g.alternate(self.ag_mop, self.ag_cron)

        self.ag_cron_current = self.ag_cron
        self.ag_mop_current = self.ag_mop

    def convert(self, offset=0, limit=None, ids=None):
        actions_logs = ActionLog.objects.filter(Q(cron=self.cron) | Q(mop=self.mop)).order_by('id')
        if limit is None:
            limit = actions_logs.count()
        count_offset = 0
        count_converted = 0
        for log in actions_logs:
            if not self.including_view_actions and log.action in self.VIEW_ACTIONS:
                continue
            if count_offset < offset:
                # skipping this log, wait until the offset is reached
                count_offset += 1
            else:
                if not ids or log.id in ids:
                    if self._convert_action_log(log):
                        count_converted += 1
                        if count_converted >= limit:
                            break  # Stop at the limit

            if log.action in self.TRUST_MODIFYING_ACTIONS:
                self.update_trust(log)

    def update_trust(self, log):
        mail = log.mail
        if mail and mail.trust:
            self.trust += mail.trust
        if log.action == ActionLog.ACTION_MOP_RECEIVE_MAIL_PERFORMANCE:
            # Resetting the trust level
            self.trust_total += self.trust
            self.trust = 0

    def get_provn(self):
        return self.prov.get_provn()

    def get_provjson(self):
        return self.prov.get_provjson()

    def _convert_action_log(self, log):
        if log.action in ActionLogProvConverter._converters:
            bundle = self.prov.bundle('b:{user_id}/{log_id}'.format(user_id=self.user.id, log_id=log.id))\
                if self.generating_bundle else self.prov

            # TODO Surround by try/except block to fail gracefully should there is any exception during conversion
            converted = self._converters[log.action](self, bundle, log)
            if self.generating_bundle:
                if converted:
                    # Cache the bundle for this action log (mainly for debugging)
                    self.cache[log.id] = bundle
                    if self.bundle_attribution:
                        # Attributing the bundle
                        bundle_id = bundle.get_identifier()
                        self.prov.entity(bundle_id, {'prov:type': PROV['Bundle']})
                        e_log = self.prov.entity('log:{log_id}'.format(log_id=log.id),
                                                 {'cron:timestamp': log.createdAt})
                        self.prov.wasAttributedTo(bundle_id, 'b:script')
                        self.prov.wasDerivedFrom(bundle_id, e_log, other_attributes={'prov:type': 'cron:provexport'})
                else:
                    # Remove the empty bundle
                    self.prov._records.remove(bundle)
                    del self.prov._bundles[bundle.get_identifier()]

            return converted
        else:
            # TODO: Emit warnings for inconvertible logs
            return False

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
            return True
        else:
            return False

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
        return True

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
        self.ag_cron = ag_cron_active
        self.ag_cron_current = ag_cron_active
        return True

    def action_cron_login(self, bundle, log):
        g = bundle
        cron = log.cron
        act = g.activity('cronact:login/{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id),
                         log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_player)

        ag_cron_logged_in = g.agent('cronuser:{cron_id}/{log_id}'.format(cron_id=cron.id, log_id=log.id))
        g.specialization(ag_cron_logged_in, self.ag_cron)
        g.wasGeneratedBy(ag_cron_logged_in, act)
        self.ag_cron_current = ag_cron_logged_in
        return True

    def _create_mission_entity(self, mission):
        g = self.prov
        e_mission_id = 'mission:{mission_id}'.format(mission_id=mission.id)
        if e_mission_id not in self.cache:
            self.cache[e_mission_id] = g.entity(e_mission_id, {'prov:label': mission.name})
        return self.cache[e_mission_id]

    def _create_mission_action(self, bundle, action, log):
        g = bundle
        mission = log.mission
        e_mission = self._create_mission_entity(mission)
        e_mission_part = g.entity(
            '{mission_id}/{action}'.format(mission_id=e_mission.get_identifier(), action=action)
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
            {'cron:mission': e_mission.get_identifier(),
             'cron:missionState': log.get_missionState_display()}
        )
        g.wasDerivedFrom(ag_cron_new, e_mission_part, act, other_attributes={'prov:type': 'cron:seen'})
        return True

    def action_cron_view_mission_intro(self, bundle, log):
        return self._create_mission_action(bundle, 'intro', log)

    def action_cron_view_mission_briefing(self, bundle, log):
        return self._create_mission_action(bundle, 'briefing', log)

    def action_cron_view_mission_debriefing(self, bundle, log):
        return self._create_mission_action(bundle, 'debriefing', log)

    def action_cron_view_mission_outro(self, bundle, log):
        return self._create_mission_action(bundle, 'outro', log)

    def _create_case_entity(self, case):
        g = self.prov
        e_case_id = 'case:{case_serial}'.format(case_serial=case.serial)
        if e_case_id not in self.cache:
            mission = case.mission
            e_mission = self._create_mission_entity(mission)
            e_case = g.entity(e_case_id, {'prov:label': case.name})
            g.hadMember(e_mission, e_case)
            self.cache[e_case_id] = e_case
        return self.cache[e_case_id]

    def _create_case_action(self, bundle, log, action):
        cron = log.cron
        case = log.case
        e_case = self._create_case_entity(case)
        e_case_part = bundle.entity(
            '{case_id}/{action}'.format(case_id=e_case.get_identifier(), action=action)
        )
        self.prov.hadMember(e_case, e_case_part)
        act = bundle.activity(
            'cronact:view_case_{action}/{case_id}/{log_id}'.format(case_id=case.id, action=action, log_id=log.id),
            log.createdAt, None,
            {'cron:action_log_id': log.id}
        )
        bundle.wasAssociatedWith(act, self.ag_cron_current)
        bundle.used(act, e_case_part)
        ag_cron_new = self._create_new_cron_entity(
            bundle, log, act,
            {'cron:case': e_case.get_identifier(),
             'cron:caseSolved': log.caseSolved}
        )
        bundle.wasDerivedFrom(ag_cron_new, e_case_part, act, other_attributes={'prov:type': 'cron:seen'})
        return True

    def action_cron_view_case_intro(self, bundle, log):
        return self._create_case_action(bundle, log, 'intro')

    def _create_cron_document_entity(self, cronDoc):
        e_cronDoc_id = 'crondoc:{serial}'.format(serial=cronDoc.serial)
        if e_cronDoc_id not in self.cache:
            e_case = self._create_case_entity(cronDoc.case)
            e_cronDoc = self.prov.entity(e_cronDoc_id, {'cron:clearance': cronDoc.clearance,
                                                        'prov:label': cronDoc.name})
            self.cache[e_cronDoc_id] = e_cronDoc
            self.prov.hadMember(e_case, e_cronDoc)
        return self.cache[e_cronDoc_id]

    def action_cron_hack_document(self, bundle, log):
        cronDoc = log.cronDocument
        act_id = 'cronact:hack_document/{doc_id}/{log_id}'.format(doc_id=cronDoc.id, log_id=log.id)
        act = bundle.activity(act_id, log.createdAt, log.modifiedAt,
                              {'cron:action_log_id': log.id, 'cron:success': log.successfulHack})
        if log.successfulHack:
            mail = log.mail
            cronDocInstance = log.cronDocumentInstance
            e_cronDoc = self._create_cron_document_entity(cronDoc)
            e_cronDocInst = bundle.entity('{cronDoc_id}/{instance_id}'.format(cronDoc_id=e_cronDoc.get_identifier(),
                                                                              instance_id=cronDocInstance.id))
            e_mail = self._create_mail_entity(bundle, mail, instance_id=log.id)
            bundle.specializationOf(e_cronDocInst, e_cronDoc)
            bundle.used(act, e_mail)
            bundle.wasGeneratedBy(e_cronDocInst, act)
            bundle.wasDerivedFrom(e_cronDocInst, e_mail, act, other_attributes={'prov:type': 'mop:mailAttachment'})
            self._create_new_cron_entity(bundle, log, act, {'cron:documents': e_cronDoc.get_identifier})
        return True

    def action_cron_view_fluff(self, bundle, log):
        return self._create_cron_activity(bundle, 'view_fluff', log.cron, log, {'cron:fluff': log.fluff})

    def _create_department_agent(self, unit):
        ag_dept_id = 'dept:{department}'.format(department=unit.serial)
        if ag_dept_id not in self.cache:
            self.cache[ag_dept_id] = self.prov.agent(ag_dept_id, {'prov:label': unit.name})
        return self.cache[ag_dept_id]

    def _create_new_mop_entity(self, bundle, log, activity=None, mop_attrs=None, derivation_type=None):
        ag_mop_new = bundle.agent('mopuser:{mop_id}/{log_id}'.format(mop_id=self.mop.id, log_id=log.id), mop_attrs)
        if mop_attrs:
            # New attribute(s), this is a revision of the current mop
            der_attrs = {'prov:type': derivation_type} if derivation_type else None
            bundle.wasRevisionOf(ag_mop_new, self.ag_mop_current, activity, other_attributes=der_attrs)
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
        return True

    def action_mop_login(self, bundle, log):
        g = bundle
        mop = log.mop
        act = g.activity('mopact:login/{mop_id}/{log_id}'.format(mop_id=mop.id, log_id=log.id),
                         log.createdAt, log.createdAt,
                         {'cron:action_log_id': log.id})
        g.wasAssociatedWith(act, self.ag_player)
        ag_mop_new = bundle.agent('mopuser:{mop_id}/{log_id}'.format(mop_id=self.mop.id, log_id=log.id))
        g.specializationOf(ag_mop_new, self.ag_mop)
        g.wasGeneratedBy(ag_mop_new, act)
        self.ag_mop_current = ag_mop_new
        return True

    def action_mop_receive_mail_tutorial(self, bundle, log):
        e_mail = self._create_mail_entity(bundle, log.mail)
        act = self._create_mop_activity(bundle, log, 'receive_mail_tutorial')
        bundle.used(act, e_mail)
        return True

    def action_mop_tutorial_progress(self, bundle, log):
        self._create_mop_activity(bundle, log, 'progress_tutorial',
                                  mop_attrs={'cron:tutorialProgress': log.tutorialProgress})
        return True

    def _create_form_blank_entity(self, bundle, form_blank, user_id=None):
        e_form_blank_id = 'form:{form_serial}'.format(form_serial=form_blank.serial)
        if user_id:
            e_form_blank_id += '/%d' % user_id
        if e_form_blank_id not in self.cache:
            self.cache[e_form_blank_id] = bundle.entity(e_form_blank_id, {'prov:label': form_blank.name})
        return self.cache[e_form_blank_id]

    def _create_form_signed_entity(self, bundle, form_signed, form_blank):
        e_form_signed_id = 'form:{form_serial}/{instance_serial}'.format(
            form_serial=form_blank.serial, instance_serial=form_signed.serial
        )
        if e_form_signed_id not in self.cache:
            self.cache[e_form_signed_id] = bundle.entity(
                e_form_signed_id, {'mop:timestamp': form_signed.createdAt, 'mop:data': form_signed.data}
            )
        return self.cache[e_form_signed_id]

    def action_mop_form_sign(self, bundle, log):
        mop = log.mop
        form_signed = log.requisitionInstance
        form_blank = form_signed.blank.requisition
        # TODO: Create a new mop or not? Probably not since the mop entity does not change after signing the form
        e_form_blank = self._create_form_blank_entity(bundle, form_blank, mop.id)
        act = bundle.activity('mopact:form/sign/{mop_id}/{instance_id}'.format(mop_id=mop.id,
                                                                               instance_id=form_signed.id),
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        bundle.used(act, e_form_blank)
        bundle.wasAssociatedWith(act, self.ag_mop_current)
        e_form_signed = self._create_form_signed_entity(bundle, form_signed, form_blank)
        bundle.wasGeneratedBy(e_form_signed, act)
        bundle.wasDerivedFrom(e_form_signed, e_form_blank, activity=act, other_attributes={'prov:type': 'mop:signForm'})
        if form_signed.data in self.cache:
            e_data = self.cache[form_signed.data]
            bundle.used(act, e_data)
            bundle.wasDerivedFrom(e_form_signed, e_data, act, other_attributes={'prov:type': 'mop:mailAttachment'})
        return True

    def _create_mop_document_entity(self, bundle, log, document_instance, activity=None, attrs=None):
        randomized_document = document_instance.randomizedDocument
        mop_document = randomized_document.mopDocument
        unit = mop_document.unit

        # TODO Perhaps a separate bundle to contain the creation of these entity is needed
        e_mop_document_id = 'asset:mop_document/{unit_serial}/{document_id}'.format(
            unit_serial=unit.serial, document_id=mop_document.id
        )
        if e_mop_document_id not in self.cache:
            self.cache[e_mop_document_id] = self.prov.entity(
                e_mop_document_id,
                {'mop:documentName': mop_document.name, 'mop:clearanceLevel': mop_document.clearance}
            )
        e_randomized_document_id = 'doc:{unit_serial}/{document_id}'.format(
            unit_serial=unit.serial, document_id=randomized_document.id)
        if e_randomized_document_id not in self.cache:
            self.cache[e_randomized_document_id] = self.prov.entity(
                e_randomized_document_id,
                {'mop:serial': randomized_document.serial}
            )
            self.prov.wasDerivedFrom(e_randomized_document_id, e_mop_document_id,
                                     other_attributes={'prov:type': 'mop:randomise'})
        e_document_instance_id = 'doc:{unit_serial}/{document_id}/{instance_id}'.format(
            unit_serial=unit.serial, document_id=randomized_document.id, instance_id=document_instance.id
        )
        if e_document_instance_id not in self.cache:
            # The instance that was created by the system
            e_document_instance = bundle.entity(e_document_instance_id, attrs)
            bundle.wasDerivedFrom(e_document_instance_id, e_randomized_document_id, activity)
            self.general_entities[e_document_instance_id] = e_document_instance
            # The instance currently using (by the caller function)
            e_document_instance_id_spe = e_document_instance_id + '/' + str(log.id)
            e_document_instance_spe = bundle.entity(e_document_instance_id_spe, attrs)
            bundle.specialization(e_document_instance_spe, e_document_instance)
            self.cache[e_document_instance_id] = e_document_instance_spe
            self.general_entities[e_document_instance_spe] = e_document_instance
        elif attrs:
            # This is an update of an existing entity
            e_prev_document_instance = self.cache[e_document_instance_id]
            e_document_instance_id_spe = e_document_instance_id + '/' + str(log.id)
            e_document_instance_spe = bundle.entity(e_document_instance_id_spe, attrs)
            bundle.wasRevisionOf(e_document_instance_id_spe, e_prev_document_instance, activity)
            self.cache[e_document_instance_id] = e_document_instance_spe
            self.general_entities[e_document_instance_spe] = self.general_entities[e_document_instance_id]
        e_document_instance = self.cache[e_document_instance_id]
        # Cache this for usage in form signing
        self.cache[document_instance.getDocumentSerial()] = e_document_instance
        return e_document_instance

    def _create_mail_entity(self, bundle, mail, attrs=None, instance_id=None):
        spe_link_needed = False
        if mail not in self.cache:
            sender = mail.unit.serial if mail.type == Mail.TYPE_RECEIVED else mail.mop_id
            e_mail_id = 'mopmail:{sender}/{mail_id}'.format(sender=sender, mail_id=mail.id)
            e_mail = bundle.entity(e_mail_id, attrs)
            self.cache[e_mail_id] = e_mail
            self.cache[mail] = e_mail
            self.general_entities[mail] = e_mail
            spe_link_needed = True

        if instance_id is not None:
            e_mail = self.general_entities[mail]
            e_mail_instance = bundle.entity('{email_id}/{instance_id}'.format(email_id=e_mail.get_identifier(),
                                                                              instance_id=instance_id))
            if spe_link_needed:
                bundle.specializationOf(e_mail_instance, e_mail)
            self.cache[mail] = e_mail_instance

        return self.cache[mail]

    def action_mop_mail_compose_with_form(self, bundle, log):
        # No need to log this action as there is no mail reference to describe the provenance!
        # The form used here will be referenced when the mail is sent
        return False

    def action_mop_mail_send(self, bundle, log):
        mop = log.mop
        mail = log.mail

        # The data accompany with the mail
        e_data = None
        if mail.requisitionInstance:
            form_signed = mail.requisitionInstance
            form_blank = form_signed.blank.requisition
            e_data = self._create_form_signed_entity(bundle, form_signed, form_blank)

        act = bundle.activity('mopact:mail/send/{mop_id}/{mail_id}'.format(mop_id=mop.id, mail_id=mail.id),
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        if e_data:
            bundle.used(act, e_data)
        bundle.wasAssociatedWith(act, self.ag_mop_current)
        e_mail = self._create_mail_entity(bundle, mail)
        # TODO: Create a new mop or not? Probably not since the mop entity does not change after sending the mail
        bundle.wasGeneratedBy(e_mail, act)
        if mail.mopDocumentInstance:
            # Just getting the current entity
            e_document_instance = self._create_mop_document_entity(bundle, log, mail.mopDocumentInstance)
            bundle.wasDerivedFrom(e_mail, e_document_instance, other_attributes={'prov:type': 'mop:mailAttachment'})

        if e_data:
            bundle.wasDerivedFrom(e_mail, e_data, act, other_attributes={'prov:type': 'mop:mailAttachment'})

        return True

    def action_mop_mail_draft(self, bundle, log):
        mop = log.mop
        mail = log.mail

        # TODO Probably need to find the previous action log that composed the email and create an activity for that
        e_mail = self._create_mail_entity(bundle, mail)
        act_id = 'mopact:mail/draft/{mop_id}/{mail_id}/{log_id}'.format(mop_id=mop.id, mail_id=mail.id, log_id=log.id)
        act = bundle.activity(act_id, log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        bundle.wasAssociatedWith(act, self.ag_mop_current)
        bundle.used(act, e_mail)

        e_mail_draft = bundle.entity('{email_id}/{log_id}'.format(email_id=e_mail.get_identifier(), log_id=log.id),
                                     {'mop:mailInDraft': True})
        bundle.wasGeneratedBy(e_mail_draft, act)
        bundle.wasRevisionOf(e_mail_draft, e_mail, act)
        return True

    def action_mop_receive_mail_form(self, bundle, log):
        mop = log.mop
        mail = log.mail
        previous_mail = mail.replyTo
        mop_attrs = {}

        # The data accompany with the mail
        if previous_mail:
            e_previous_mail = self._create_mail_entity(bundle, previous_mail)

        if mail.subject != Mail.SUBJECT_RECEIVE_FORM:
            raise Exception('Wrong mail type encountered: %s' % mail.get_subject_display())
        form_blank = mail.requisitionBlank.requisition
        e_form = self._create_form_blank_entity(bundle, form_blank)
        e_form_instance = self._create_form_blank_entity(bundle, form_blank, mop.id)
        mop_attrs['mop:forms'] = e_form.get_identifier()

        ag_dept = self._create_department_agent(mail.unit)
        act = bundle.activity('mopact:form/assign/{mop_id}/{log_id}'.format(mop_id=mop.id, log_id=log.id),
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        if previous_mail:
            bundle.used(act, e_previous_mail)
        bundle.used(act, e_form)
        bundle.wasGeneratedBy(e_form_instance, act)
        bundle.specializationOf(e_form_instance, e_form)
        bundle.wasAssociatedWith(act, ag_dept)
        e_mail = self._create_mail_entity(bundle, mail, {'mop:mail_subject': mail.get_subject_display()})

        bundle.wasGeneratedBy(e_mail, act)
        if previous_mail:
            bundle.wasDerivedFrom(e_mail, e_previous_mail, act, other_attributes={'prov:type': 'mop:replyTo'})

        self._create_new_mop_entity(bundle, log, act, mop_attrs)
        return True

    def action_mop_receive_mail_document(self, bundle, log):
        # TODO: This action should be about app:mop generating document for the mop player
        mop = log.mop
        mail = log.mail
        previous_mail = mail.replyTo
        mop_attrs = {}

        if mail.subject != Mail.SUBJECT_RECEIVE_DOCUMENT:
            raise Exception('Wrong mail type encountered: %s' % mail.get_subject_display())

        if mail.trust:
            mop_attrs['mop:trust'] = self.trust + mail.trust
        document_instance = mail.mopDocumentInstance
        if document_instance is None or document_instance.randomizedDocument is None:
            # TODO Raise an exception here
            return
        e_document_instance_spe = self._create_mop_document_entity(bundle, log, document_instance)
        e_document_instance_gen = self.general_entities[e_document_instance_spe]
        # TODO: Create an activity that generated e_document_instance
        mop_attrs['mop:documents'] = e_document_instance_gen.get_identifier()

        act = bundle.activity('mopact:document/assign/{mop_id}/{doc_id}'.format(mop_id=mop.id,
                                                                                doc_id=document_instance.id),
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        bundle.used(act, e_document_instance_gen)
        ag_dept = self._create_department_agent(mail.unit)
        bundle.wasAssociatedWith(act, ag_dept)
        e_mail = self._create_mail_entity(bundle, mail, {'mop:mail_subject': mail.get_subject_display()})

        bundle.wasGeneratedBy(e_mail, act)
        if previous_mail:
            e_previous_mail = self._create_mail_entity(bundle, previous_mail)
            bundle.used(act, e_previous_mail)
            bundle.wasDerivedFrom(e_mail, e_previous_mail, act, other_attributes={'prov:type': 'mop:replyTo'})

        bundle.wasDerivedFrom(e_mail, e_document_instance_gen, act,
                              other_attributes={'prov:type': 'mop:mailAttachment'})
        bundle.wasDerivedFrom(e_document_instance_spe, e_mail, act,
                              other_attributes={'prov:type': 'mop:mailAttachment'})

        self._create_new_mop_entity(bundle, log, act, mop_attrs)
        return True

    def _create_trust_mail_activity(self, bundle, log, action):
        mop = log.mop
        mail = log.mail
        mop_attrs = {
            'mop:trust': self.trust + mail.trust
        }
        ag_dept = self._create_department_agent(mail.unit)
        act_id = 'mopact:performance/{action}/{mop_id}/{log_id}'.format(action=action, mop_id=mop.id, log_id=log.id)
        act = bundle.activity(act_id, log.createdAt, log.createdAt, {'cron:action_log_id': log.id})
        bundle.used(act, self.ag_mop_current)
        bundle.wasAssociatedWith(act, ag_dept)
        e_mail = self._create_mail_entity(bundle, mail, {'mop:mail_subject': mail.get_subject_display()})
        bundle.wasGeneratedBy(e_mail, act)

        if mail.replyTo:
            e_previous_mail = self._create_mail_entity(bundle, mail.replyTo)
            bundle.used(act, e_previous_mail)
            bundle.wasDerivedFrom(e_mail, e_previous_mail, act, other_attributes={'prov:type': 'mop:replyTo'})

        self._create_new_mop_entity(bundle, log, act, mop_attrs)
        return act

    def action_mop_receive_mail_report(self, bundle, log):
        if log.mail.subject != Mail.SUBJECT_REPORT_EVALUATION:
            raise Exception('Wrong mail type encountered: %s' % log.mail.get_subject_display())

        self._create_trust_mail_activity(bundle, log, 'update')
        return True

    def action_mop_receive_mail_error(self, bundle, log):
        if log.mail.subject != Mail.SUBJECT_ERROR:
            raise Exception('Wrong mail type encountered: %s' % log.mail.get_subject_display())
        self._create_trust_mail_activity(bundle, log, 'penalty')
        return True

    def action_mop_receive_mail_performance(self, bundle, log):
        mop = log.mop
        mail = log.mail
        performance = mail.performanceInstance
        action = performance.get_type_display()
        level = performance.get_result_display()
        mop_attrs = {
            'mop:trust': 0,
            'mop:trust_total': self.trust_total + performance.trust,
            'mop:credits': performance.credit
        }
        if performance.type != PerformanceInstance.TYPE_NEUTRAL:
            # There is a change in clearance level
            mop_attrs['mop:clearance'] = level

        ag_dept = self._create_department_agent(mail.unit)
        act_id = 'mopact:performance/{action}/{mop_id}/{log_id}'.format(action=action, mop_id=mop.id, log_id=mail.id)
        act = bundle.activity(act_id, performance.createdAt, log.modifiedAt,
                              {'cron:action_log_id': log.id, 'mop:reviewPeriod': performance.period.id})
        bundle.used(act, self.ag_mop_current)
        bundle.wasAssociatedWith(act, ag_dept)
        e_mail = self._create_mail_entity(bundle, mail, {'mop:mail_subject': mail.get_subject_display()})

        bundle.wasGeneratedBy(e_mail, act)

        self._create_new_mop_entity(bundle, log, act, mop_attrs)
        return True

    def action_mop_receive_mail_manual(self, bundle, log):
        mop = log.mop
        mail = log.mail
        mop_attrs = {}
        ag_dept = self._create_department_agent(mail.unit)
        if mail.trust:
            mop_attrs['mop:trust'] = self.trust + mail.trust
            act_id = 'mopact:performance/manual/{mop_id}/{log_id}'.format(mop_id=mop.id, log_id=mail.id)
        else:
            act_id = 'mopact:mail/manual/{mop_id}/{log_id}'.format(mop_id=mop.id, log_id=mail.id)

        act = bundle.activity(act_id, log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        bundle.wasAssociatedWith(act, ag_dept)
        if mail.trust:
            bundle.used(act, self.ag_mop_current)

        e_mail = self._create_mail_entity(bundle, mail, {'mop:mail_subject': mail.get_subject_display()})
        bundle.wasGeneratedBy(e_mail, act)

        self._create_new_mop_entity(bundle, log, act, mop_attrs)
        return True

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
        return True

    def action_mop_view_provenance(self, bundle, log):
        mop = log.mop
        document = log.mopDocumentInstance
        correct = log.mopDocumentInstanceCorrect

        if document is None:
            # The reference to the document was not recorded, nothing to do
            return
        # TODO Reference to prov_log to see if this is just a simple view or the graph has been manipulated
        # Just getting the document's current entity
        e_document = self._create_mop_document_entity(bundle, log, document)

        act_id = 'mopact:provenance/view/{mop_id}/{doc_id}/{log_id}'.format(
            mop_id=mop.id, doc_id=document.id, log_id=log.id
        )
        act = bundle.activity(act_id,
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        bundle.used(act, e_document)
        bundle.wasAssociatedWith(act, self.ag_mop_current)

        # self._create_new_mop_entity(bundle, log, act, {'mop:documents': e_document.get_identifier()})
        return True

    def action_mop_provenance_submit(self, bundle, log):
        mop = log.mop
        document = log.mopDocumentInstance
        correct = log.mopDocumentInstanceCorrect

        if document is None:
            # The reference to the document was not recorded, nothing to do
            return

        # Hack to get the previous instance (i.e. before submission) by using an empty 'attrs' parameter
        e_document_prev = self._create_mop_document_entity(bundle, log, document)

        act_id = 'mopact:provenance/submit/{mop_id}/{doc_id}/{log_id}'.format(
            mop_id=mop.id, doc_id=document.id, log_id=log.id
        )
        act = bundle.activity(act_id,
                              log.createdAt, log.createdAt,
                              {'cron:action_log_id': log.id})
        bundle.used(act, e_document_prev)
        e_document = self._create_mop_document_entity(bundle, log, document, act,
                                                      {'mop:provenanceCorrectness': correct})
        bundle.wasGeneratedBy(e_document, act)
        bundle.wasAssociatedWith(act, self.ag_mop_current)

        self._create_new_mop_entity(bundle, log, act, {'mop:documents_submitted': e_document.get_identifier()})
        return True

    def ignored_log(self, bundle, log):
        # No provenance to be generated in this function
        return False

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
        ActionLog.ACTION_CRON_VIEW_FLUFF:               action_cron_view_fluff,
        ActionLog.ACTION_CRON_VIEW_MISSION_INTRO:       action_cron_view_mission_intro,
        ActionLog.ACTION_CRON_VIEW_MISSION_BRIEFING:    action_cron_view_mission_briefing,
        ActionLog.ACTION_CRON_VIEW_MISSION_CASES:       _create_action_cron_view_function('mission_cases'),
        ActionLog.ACTION_CRON_VIEW_MISSION_DEBRIEFING:  action_cron_view_mission_debriefing,
        ActionLog.ACTION_CRON_VIEW_MISSION_OUTRO:       action_cron_view_mission_outro,
        ActionLog.ACTION_CRON_VIEW_CASE_INTRO:          action_cron_view_case_intro,
        ActionLog.ACTION_CRON_HACK_DOCUMENT:            action_cron_hack_document,

        ActionLog.ACTION_MOP_CREATED:                   action_mop_created,
        ActionLog.ACTION_MOP_LOGIN:                     action_mop_login,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_TUTORIAL:     action_mop_receive_mail_tutorial,
        ActionLog.ACTION_MOP_TUTORIAL_PROGRESS:         action_mop_tutorial_progress,
        ActionLog.ACTION_MOP_VIEW_INDEX:                _create_action_mop_view_function('index'),
        ActionLog.ACTION_MOP_VIEW_GUIDEBOOK:            _create_action_mop_view_function('guidebook'),
        ActionLog.ACTION_MOP_VIEW_PERFORMANCE:          _create_action_mop_view_function('performance'),
        ActionLog.ACTION_MOP_VIEW_COMPOSE:              ignored_log,
        ActionLog.ACTION_MOP_VIEW_INBOX:                _create_action_mop_view_function('inbox'),
        ActionLog.ACTION_MOP_VIEW_OUTBOX:               _create_action_mop_view_function('outbox'),
        ActionLog.ACTION_MOP_VIEW_TRASH:                _create_action_mop_view_function('trash'),
        ActionLog.ACTION_MOP_VIEW_DRAFT:                _create_action_mop_view_function('draft'),
        ActionLog.ACTION_MOP_VIEW_FORMS_BLANKS:         _create_action_mop_view_function('forms_blank'),
        ActionLog.ACTION_MOP_VIEW_FORMS_FILL:           _create_action_mop_view_function('forms_fill'),
        ActionLog.ACTION_MOP_VIEW_FORMS_SIGNED:         _create_action_mop_view_function('forms_signed'),
        ActionLog.ACTION_MOP_VIEW_DOCUMENTS_POOL:       _create_action_mop_view_function('documents_pool'),
        ActionLog.ACTION_MOP_VIEW_DOCUMENTS_DRAWER:     _create_action_mop_view_function('documents_drawer'),
        ActionLog.ACTION_MOP_VIEW_DOCUMENTS_ARCHIVE:    _create_action_mop_view_function('documents_archive'),
        ActionLog.ACTION_MOP_FORM_SIGN:                 action_mop_form_sign,
        ActionLog.ACTION_MOP_MAIL_COMPOSE_WITH_FORM:    action_mop_mail_compose_with_form,
        ActionLog.ACTION_MOP_MAIL_SEND:                 action_mop_mail_send,
        ActionLog.ACTION_MOP_MAIL_DRAFT:                action_mop_mail_draft,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_ERROR:        action_mop_receive_mail_error,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_FORM:         action_mop_receive_mail_form,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_DOCUMENT:     action_mop_receive_mail_document,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_REPORT:       action_mop_receive_mail_report,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_PERFORMANCE:  action_mop_receive_mail_performance,
        ActionLog.ACTION_MOP_RECEIVE_MAIL_MANUAL:       action_mop_receive_mail_manual,
        ActionLog.ACTION_MOP_VIEW_MAIL:                 action_mop_view_mail,
        ActionLog.ACTION_MOP_VIEW_PROVENANCE:           action_mop_view_provenance,
        ActionLog.ACTION_MOP_PROVENANCE_SUBMIT:         action_mop_provenance_submit,
    }
