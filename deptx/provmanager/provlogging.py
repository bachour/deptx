from prov.model import ProvBundle, Namespace, Identifier
#from .models import ProvenanceLog
from .views import API
from deptx.helpers import generateUUID

import datetime
import time

DEFAULT_NAMESPACES = {
    'cron': 'http://www.cr0n.org/ns#',
    'server': 'http://www.cr0n.org/server/',
    'act': 'http://www.cr0n.org/ns#act',
    'asset': 'http://www.cr0n.org/ns#asset',
    'log': 'http://www.cr0n.org/log/',
    'b': 'http://www.cr0n.org/bundles/',
    'cronuser': 'http://www.cr0n.org/user/',
    'mopuser': 'http://www.mofp.org/user/',
    'mop': 'http://mofp.net/ns#',
    'dept': 'http://mofp.net/departments/',
    'form': 'http://mofp.net/forms/',
    'doc': 'http://mofp.net/documents/',
    'foaf': 'http://xmlns.com/foaf/0.1/',  # see http://xmlns.com/foaf/spec/
}

# Case, Document, Node, Property, Form, Account, User,

URI = Identifier


def getStoreId(cron):
    return 0
#     try:
#         provLog = ProvenanceLog.objects.get(cron=cron)
#     except ProvenanceLog.DoesNotExist:
#         provLog = None
# 
#     return provLog.store_id


def addBundle(cron, bundle, bundle_id):
    store_id = getStoreId(cron)
    #TODO bundle_id is problematic when logging in without having logged out on the mop-page as it does not support auto-logon
    bundle_id = bundle_id + "/" + str(time.time())  # Is this really needed?
    #API.add_bundle(store_id, bundle, bundle_id)


def provlog_add_cron_register(cron):
    bundle_id, bundle = create_bundle_cron_register(cron)
    store_id = API.submit_document(bundle, bundle_id, public=False)
    provLog = ProvenanceLog(cron=cron)
    provLog.store_id = store_id
    provLog.save()


def provlog_add_cron_login(cron, session_key):
    bundle_id, bundle = create_bundle_cron_login(cron.id, session_key)
    addBundle(cron, bundle, bundle_id)


def provlog_add_cron_logout(cron, session_key):
    bundle_id, bundle = create_bundle_cron_logout(cron.id, session_key)
    addBundle(cron, bundle, bundle_id)


def provlog_add_mop_register(cron, mop, session_key):
    bundle_id, bundle = create_bundle_mop_register(cron, mop, session_key)
    addBundle(cron, bundle, bundle_id)


def provlog_add_mop_login(mop, session_key):
    bundle_id, bundle = create_bundle_mop_login(mop.id, session_key)
    addBundle(mop.cron, bundle, bundle_id)


def provlog_add_mop_logout(mop, session_key):
    bundle_id, bundle = create_bundle_mop_logout(mop.id, session_key)
    addBundle(mop.cron, bundle, bundle_id)


def provlog_add_mop_sign_form(mop, requisitionInstance, session_key):
    bundle_id, bundle = create_bundle_mop_sign_form(mop.id, session_key, requisitionInstance.blank.requisition.serial, requisitionInstance.id, requisitionInstance.data)
    addBundle(mop.cron, bundle, bundle_id)


def provlog_add_mop_send_form(mop, mail, session_key):
    bundle_id, bundle = create_bundle_mop_send_form(mop.id, session_key, mail.requisitionInstance.id, mail.requisitionInstance.blank.requisition.serial, mail.id, mail.unit.serial)
    addBundle(mop.cron, bundle, bundle_id)


def provlog_add_mop_issue_form(mop, mail, new_requisition, session_key):
    bundle_id, bundle = create_bundle_mop_issue_form(mop.id, session_key, mail.requisitionInstance.id, mail.requisitionInstance.blank.requisition.serial, mail.id, new_requisition.serial, mail.unit.serial)
    addBundle(mop.cron, bundle, bundle_id)


def provlog_add_mop_issue_document(mop, mail, mopDocumentInstance, session_key):
    bundle_id, bundle = create_bundle_mop_issue_document(mop.id, session_key, mail.id, mail.requisitionInstance.blank.requisition.serial, mail.requisitionInstance.id, mopDocumentInstance.getDocumentSerial(), mopDocumentInstance.id, mail.unit.serial)
    addBundle(mop.cron, bundle, bundle_id)


def create_bundle_cron_register(cron):
    '''An cron user account is created'''
    bundle_id = 'b:registration/%d' % cron.id
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    s = b.agent("server:1")
    u = b.agent('cronuser:%d' % cron.id, [('foaf:name', cron.user.username)])
    now = datetime.datetime.now()
    a = b.activity('log:%d/register' % cron.id, now, now, other_attributes=[('prov:type', 'act:CronAccountRegistration')])
    b.wasGeneratedBy(u, a)
    b.wasAssociatedWith(a, s)
    return bundle_id, b


def create_bundle_mop_register(cron, mop, session_key):
    '''An mop user account is created'''
    bundle_id = 'b:registration/%d' % mop.id
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    s = b.agent('cronuser:%d/%s' % (cron.id, session_key))
    u = b.agent('mopuser:%d' % mop.id, [('foaf:name', mop.user.username)])
    now = datetime.datetime.now()
    a = b.activity('log:%d/register' % mop.id, now, now, other_attributes=[('prov:type', 'act:MopAccountRegistration')])
    b.wasGeneratedBy(u, a)
    b.wasAssociatedWith(a, s)
    return bundle_id, b


def create_bundle_cron_login(user_id, session_key):
    '''User id 2 logs into the system'''
    bundle_id = 'b:%s/login' % session_key
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    u = b.agent('cronuser:%d' % user_id)
    ag = b.agent('cronuser:%d/%s' % (user_id, session_key))
    now = datetime.datetime.now()
    a = b.activity('log:%d/login/%s' % (user_id, session_key), now, now, other_attributes=[('prov:type', 'act:CronAccountLogin')])
    b.wasAssociatedWith(a, u)
    b.wasGeneratedBy(ag, a)
    b.specializationOf(ag, u)
    return bundle_id, b


def create_bundle_cron_logout(user_id, session_key):
    bundle_id = 'b:%s/logout' % session_key
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    b.add_namespace('ns', b.valid_identifier(bundle_id + '/').get_uri())

    ag = b.agent('cronuser:%d/%s' % (user_id, session_key))
    now = datetime.datetime.now()
    a = b.activity('log:%d/logout/%s' % (user_id, session_key), now, now, other_attributes=[('prov:type', 'act:CronAccountLogout')])
    b.wasInvalidatedBy(ag, a)  # This user+session no longer exists after this
    return bundle_id, b


def create_bundle_mop_login(user_id, session_key):
    '''User id 2 logs into the system'''
    bundle_id = 'b:%s/login' % session_key
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    u = b.agent('mopuser:%d' % user_id)
    ag = b.agent('mopuser:%d/%s' % (user_id, session_key))
    now = datetime.datetime.now()
    a = b.activity('log:%d/login/%s' % (user_id, session_key), now, now, other_attributes=[('prov:type', 'act:MopAccountLogin')])
    b.wasAssociatedWith(a, u)
    b.wasGeneratedBy(ag, a)
    b.specializationOf(ag, u)
    return bundle_id, b


def create_bundle_mop_logout(user_id, session_key):
    bundle_id = 'b:%s/logout' % session_key
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    b.add_namespace('ns', b.valid_identifier(bundle_id + '/').get_uri())

    ag = b.agent('mopuser:%d/%s' % (user_id, session_key))
    now = datetime.datetime.now()
    a = b.activity('log:%d/login/%s' % (user_id, session_key), now, now, other_attributes=[('prov:type', 'act:MopAccountLogout')])
    b.wasInvalidatedBy(ag, a)  # This user+session no longer exists after this
    return bundle_id, b


def create_bundle_mop_sign_form(user_id, session_key, blank_form_serial, signed_form_id, form_data=None):
    bundle_id = 'b:%s/form/signing/%d' % (session_key, signed_form_id)
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    b.add_namespace('ns', b.valid_identifier(bundle_id + '/').get_uri())

    ag = b.agent('mopuser:%d/%s' % (user_id, session_key))
    bf = b.entity('form:blank/%s' % blank_form_serial, [('prov:type', 'asset:BlankForm')])
    now = datetime.datetime.now()
    a = b.activity('ns:sign-form/%s' % blank_form_serial, now, now)
    b.wasAssociatedWith(a, ag)
    b.used(a, bf)
    data = {'prov:type': 'asset:SignedForm'}
    # Add relevant extra data of the form here
    if form_data is not None:
        data['mop:data'] = form_data
    sf = b.entity('form:signed/%s/%d' % (blank_form_serial, signed_form_id), data)
    b.wasGeneratedBy(sf, a)
    b.wasAttributedTo(sf, ag)
    return bundle_id, b


def create_bundle_mop_send_form(user_id, session_key, signed_form_id, blank_form_serial, email_id, unit_serial):
    bundle_id = 'b:%s/form/sending/%d' % (session_key, email_id)
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    b.add_namespace('ns', b.valid_identifier(bundle_id + '/').get_uri())

    ag = b.agent('mopuser:%d/%s' % (user_id, session_key))
    em = b.entity('email:%d' % email_id, [('prov:type', 'mop:Email'), ('mop:mailto', unit_serial)])
    sf = b.entity('form:signed/%s/%d' % (blank_form_serial, signed_form_id), [('prov:type', 'asset:SignedForm')])  # Add relevant extra data of the form here
    now = datetime.datetime.now()
    b.wasDerivedFrom(em, sf, time=now)
    b.wasAttributedTo(em, ag)
    return bundle_id, b


def create_bundle_mop_issue_form(user_id, session_key, signed_form_id, old_blank_form_serial, email_id, new_blank_form_serial, unit_serial):
#     t = long(time.time())
    bundle_id = 'b:%s/form/issue/%s' % (session_key, new_blank_form_serial)
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    b.add_namespace('ns', b.valid_identifier(bundle_id + '/').get_uri())

    ag = b.agent('dept:%s' % unit_serial)
    sf = b.entity('form:signed/%s/%d' % (old_blank_form_serial, signed_form_id))
    em = b.entity('email:%d' % email_id)
    now = datetime.datetime.now()
    a = b.activity('bs:issue-form/%s' % new_blank_form_serial, now, now)
    b.wasAssociatedWith(a, ag)
    b.used(a, em)
    nf = b.entity('form:blank/%s' % new_blank_form_serial)
    b.wasGeneratedBy(nf, a)
    b.wasDerivedFrom(nf, sf)
    return bundle_id, b


def create_bundle_mop_issue_document(user_id, session_key, email_id, blank_form_serial, signed_form_id, document_serial, document_instance_id, unit_serial):
    bundle_id = 'b:%s/document/issue/%s' % (session_key, document_instance_id)
    b = ProvBundle(namespaces=DEFAULT_NAMESPACES)
    b.add_namespace('ns', b.valid_identifier(bundle_id + '/').get_uri())

    ag = b.agent('dept:%s' % unit_serial)
    sf = b.entity('form:signed/%s/%d' % (blank_form_serial, signed_form_id))
    em = b.entity('email:%d' % email_id)
    now = datetime.datetime.now()
    a = b.activity('bs:issue-document/%d' % document_instance_id, now, now)
    b.wasAssociatedWith(a, ag)
    b.used(a, em)
    d = b.entity('document:%s' % document_serial, [('prov:type', 'asset:Document')])
    b.used(a, d)
    di = b.entity('document:%s/%d' % (document_serial, document_instance_id), [('prov:type', 'asset:MopDocumentInstance')])
    b.wasGeneratedBy(di, a)
    b.wasDerivedFrom(di, sf)
    b.wasDerivedFrom(di, d)
    return bundle_id, b
