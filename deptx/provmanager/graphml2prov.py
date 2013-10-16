#!/usr/local/bin/python2.7
# encoding: utf-8
'''
converter -- GraphML to PROV extraction tool

converter is a tool for extracting PROV annotations from a graphML file

@author:     Trung Dong Huynh

@copyright:  2013 University of Southampton, United Kingdom. All rights reserved.

@license:    TBD

@contact:    trungdong@donggiang.com
@deffield    updated: 2013-10-15
'''

import codecs
import sys
import os
import logging
import traceback
import urllib2
import datetime
from StringIO import StringIO
from prov.model import ProvException, PROV
logger = logging.getLogger(__name__)
import re
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

import xml.etree.ElementTree as etree

import prov.model

__all__ = []
__version__ = 0.1
__date__ = '2013-09-09'
__updated__ = '2013-09-16'

DEBUG = 1
TESTRUN = 0
PROFILE = 0


def logging_intercept(fn, level=logging.DEBUG):
    def wrapping_fn(*args, **kwargs):
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)  # 1000 should be enough for a small function
        handler.setLevel(level=level)
        logger.addHandler(handler)  # Use the existing logger, but could also use the global logger
        result = fn(*args, **kwargs)
        logger.removeHandler(handler)
        logs = log_stream.getvalue()
        log_stream.close()

        # Do whatever we want with the logs here
        return result
#         return result, logs  # We could also return the logs along with the actual result
    return wrapping_fn


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg

URL_VALIDATOR_SERVICE = 'https://provenance.ecs.soton.ac.uk/validator/provapi/documents/'

NS_URI_GRAPH_ML = 'http://graphml.graphdrawing.org/xmlns'
NS_URI_YWORKS = 'http://www.yworks.com/xml/graphml'

GRAPHML_PREFIXES = {
    'g': NS_URI_GRAPH_ML,
    'y': NS_URI_YWORKS,
}

GRAPH_ML_KEY = etree.QName(NS_URI_GRAPH_ML, 'key')
GRAPH_ML_GRAPH = etree.QName(NS_URI_GRAPH_ML, 'graph')
GRAPH_ML_NODE = etree.QName(NS_URI_GRAPH_ML, 'node')
GRAPH_ML_EDGE = etree.QName(NS_URI_GRAPH_ML, 'edge')
GRAPH_ML_DATA = etree.QName(NS_URI_GRAPH_ML, 'data')


NS_MOP = prov.model.Namespace('mop', 'http://mofp.net/ns#')
CUSTOM_ATTRIBUTES = {
    'Role': PROV['role'],
    'date_of_birth': NS_MOP['birthdate'],
}

MOP_start_date = NS_MOP['start_date']
MOP_end_date = NS_MOP['end_date']
MOP_start_time = NS_MOP['start_time']
MOP_end_time = NS_MOP['end_time']

EDGE_PROV_CODE = {
    '0': prov.model.PROV_REC_ASSOCIATION,
    '1': prov.model.PROV_REC_ATTRIBUTION,
    '2': prov.model.PROV_REC_USAGE,
    '3': prov.model.PROV_REC_DERIVATION,
    '4': prov.model.PROV_REC_GENERATION,
    '5': prov.model.PROV_REC_DELEGATION,
    '6': prov.model.PROV_REC_COMMUNICATION,
    '7': prov.model.PROV_REC_INFLUENCE,
    '8': prov.model.PROV_REC_INVALIDATION,
    '9': prov.model.PROV_REC_START,
    '10': prov.model.PROV_REC_END,
    '11': prov.model.PROV_REC_ALTERNATE,
    '12': prov.model.PROV_REC_SPECIALIZATION,
    '13': prov.model.PROV_REC_MEMBERSHIP,
}

PROV_RELATION_FUNCTION = {
    prov.model.PROV_REC_GENERATION:           prov.model.ProvBundle.generation,  # IGNORE:E241
    prov.model.PROV_REC_USAGE:                prov.model.ProvBundle.usage,
    prov.model.PROV_REC_COMMUNICATION:        prov.model.ProvBundle.communication,
    prov.model.PROV_REC_START:                prov.model.ProvBundle.start,
    prov.model.PROV_REC_END:                  prov.model.ProvBundle.end,
    prov.model.PROV_REC_INVALIDATION:         prov.model.ProvBundle.invalidation,
    prov.model.PROV_REC_DERIVATION:           prov.model.ProvBundle.derivation,
    prov.model.PROV_REC_ATTRIBUTION:          prov.model.ProvBundle.attribution,
    prov.model.PROV_REC_ASSOCIATION:          prov.model.ProvBundle.association,
    prov.model.PROV_REC_DELEGATION:           prov.model.ProvBundle.delegation,
    prov.model.PROV_REC_INFLUENCE:            prov.model.ProvBundle.influence,
    prov.model.PROV_REC_ALTERNATE:            prov.model.ProvBundle.alternate,
    prov.model.PROV_REC_SPECIALIZATION:       prov.model.ProvBundle.specialization,
    prov.model.PROV_REC_MENTION:              prov.model.ProvBundle.mention,
    prov.model.PROV_REC_MEMBERSHIP:           prov.model.ProvBundle.membership,
}

PROV_DEFAULT_RELATION = {
    (prov.model.PROV_REC_ENTITY, prov.model.PROV_REC_ENTITY): prov.model.PROV_REC_DERIVATION,
    (prov.model.PROV_REC_ENTITY, prov.model.PROV_REC_AGENT): prov.model.PROV_REC_ATTRIBUTION,
    (prov.model.PROV_REC_ENTITY, prov.model.PROV_REC_ACTIVITY): prov.model.PROV_REC_GENERATION,
    (prov.model.PROV_REC_AGENT, prov.model.PROV_REC_AGENT): prov.model.PROV_REC_DELEGATION,
    (prov.model.PROV_REC_ACTIVITY, prov.model.PROV_REC_ENTITY): prov.model.PROV_REC_USAGE,
    (prov.model.PROV_REC_ACTIVITY, prov.model.PROV_REC_AGENT): prov.model.PROV_REC_ASSOCIATION,
    (prov.model.PROV_REC_ACTIVITY, prov.model.PROV_REC_ACTIVITY): prov.model.PROV_REC_COMMUNICATION,
}


def to_unicode_or_bust(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj


def convert_attribute_name(name):
    colon_pos = name.find(': ')
    attr_name = name if colon_pos < 0 else name[colon_pos + 2:]
    # Normalising the name
    attr_name = re.sub(r"\W+", '_', attr_name.lower())
    if attr_name in CUSTOM_ATTRIBUTES:
        return CUSTOM_ATTRIBUTES[attr_name]
    else:
        return NS_MOP[attr_name]


def convert_identifier(identifier):
    localpart = re.sub(r"\W+", '_', identifier)
    return NS_MOP[localpart]


def convert_attributes(element, attributes):
        results = {}
        for data in element.iter(GRAPH_ML_DATA):
            key = data.attrib['key']
            if key in attributes:
                value = data.text
                if value:
                    # Converting custom (free) attributes in the form of <attr_name>:<attr_value>
                    if str(attributes[key]).find('free') >= 0:
                        attr_name, attr_value = value.split(':', 1)
                        attr_name = convert_attribute_name(attr_name)
                        results[attr_name] = to_unicode_or_bust(attr_value) if attr_value else ""
                    else:
                        results[attributes[key]] = to_unicode_or_bust(value)
        return results


def convert_time(date, time):
    str_datetime = ' '.join((date, time))
    return datetime.datetime.strptime(str_datetime, '%d/%m/%Y %H:%M')


class GraphMLProvConverter(object):
    def __init__(self, root):
        self.root = root
        self.initialise_attributes()

        self.prov = prov.model.ProvBundle()
        self.nodes = {}

        self.identifiers = set()

        # Getting the graph element
        self.graph = self.root.find('g:graph', GRAPHML_PREFIXES)
        # Converting nodes
        for node in self.graph.iter(GRAPH_ML_NODE):
            self.convert_node(node)
        # Converting edges
        for edge in self.graph.iter(GRAPH_ML_EDGE):
            self.convert_edge(edge)

    def initialise_attributes(self):
        # Looking for data properties
        self.node_attributes = {}
        self.edge_attributes = {}
        for key in self.root.iter(GRAPH_ML_KEY):
            if 'attr.name' in key.attrib:
                if key.attrib['attr.name'] == 'Type' and key.attrib['attr.type'] == 'int' and key.attrib['for'] == 'edge':
                    self.edge_type_key = key.attrib['id']
                    continue  # Skip this special attribute
                # Processing custom data attribute
                attributes = self.node_attributes if key.attrib['for'] == 'node' else self.edge_attributes
                attributes[key.attrib['id']] = convert_attribute_name(key.attrib['attr.name'])
            elif 'yfiles.type' in key.attrib:
                if key.attrib['for'] == 'node':
                    self.node_shape_key = key.attrib['id']
                elif key.attrib['for'] == 'edge':
                    self.edge_shape_key = key.attrib['id']

    def convert_node(self, node):
        node_id = node.attrib['id']
        logger.debug("Processing node %s" % node_id)
        label_element = node.find('g:data/y:ShapeNode/y:NodeLabel', GRAPHML_PREFIXES)
        label = to_unicode_or_bust(label_element.text)
        if not label:
            logger.warn("No label found for node %s. Ignored this node." % node_id)
            return  # Stop processing
        # Generating identifier
        identifier = convert_identifier(label)
        if identifier in self.identifiers:
            identifier = convert_identifier(label + node_id)
        self.identifiers.add(identifier)

        attributes = convert_attributes(node, self.node_attributes)
        # Adding the original label as prov:label
        attributes[prov.model.PROV['label']] = label
        shape_element = node.find('g:data/y:ShapeNode/y:Shape', GRAPHML_PREFIXES)
        shape = shape_element.attrib['type']
        # TODO: Change the following back to PROV node shape convention
        if shape == 'ellipse':
            prov_node = self.convert_entity(identifier, attributes)
        elif shape == 'rectangle':
            prov_node = self.convert_activity(identifier, attributes)
        elif shape == 'trapezoid':
            prov_node = self.convert_agent(identifier, attributes)
        else:
            logger.warn("Unrecognised shape %s. Ignored node %s (%s)." % (shape, node_id, label))
            return  # Stop processing
        # A node is converted
        self.nodes[node_id] = prov_node

    def convert_edge(self, edge):
        edge_id = edge.attrib['id']
        logger.debug("Processing edge %s" % edge_id)
        source_id = edge.attrib['source']
        target_id = edge.attrib['target']
        source_rec = self.nodes[source_id]
        target_rec = self.nodes[target_id]

        edge_type_data = edge.find("g:data[@key='%s']" % self.edge_type_key, GRAPHML_PREFIXES)
        edge_type = edge_type_data.text if edge_type_data is not None else None
        if not edge_type or edge_type not in EDGE_PROV_CODE or edge_type not in EDGE_PROV_CODE:
            # Trying to find a default relation
            try:
                prov_type = PROV_DEFAULT_RELATION[(source_rec.get_type(), target_rec.get_type())]
                logger.info('Cannot determine the PROV relation (%s) for edge %s, creating the default relation (%s) for this edge.' % (edge_type, edge_id, prov.model.PROV_N_MAP[prov_type]))
            except KeyError:
                logger.warn('Cannot determine the PROV relation (%s) for edge %s. Ignored this edge.' % (edge_type, edge_id))
                return  # Stop processing
        else:
            prov_type = EDGE_PROV_CODE[edge_type]
        attributes = convert_attributes(edge, self.edge_attributes)
        # Checking for missing prov:role
        if PROV['role'] not in attributes:
            logger.warn("A role was not specified for edge %s" % edge_id)
        try:
            PROV_RELATION_FUNCTION[prov_type](self.prov, source_rec, target_rec, other_attributes=attributes)
        except ProvException, e:
            logger.warn("Cannot create relation for edge %s (type %s - %s). Ignored this edge.\n%s" % (edge_id, edge_type, prov.model.PROV_N_MAP[prov_type], repr(e)))

    def convert_entity(self, identifier, attributes):
        return self.prov.entity(identifier, other_attributes=attributes)

    def convert_activity(self, identifier, attributes):
        start_time = None
        end_time = None
        if MOP_start_date in attributes and MOP_start_time in attributes:
            start_time = convert_time(attributes[MOP_start_date], attributes[MOP_start_time])
        if MOP_end_date in attributes and MOP_end_time in attributes:
            end_time = convert_time(attributes[MOP_end_date], attributes[MOP_end_time])
        return self.prov.activity(identifier, start_time, end_time, other_attributes=attributes)

    def convert_agent(self, identifier, attributes):
        return self.prov.agent(identifier, other_attributes=attributes)


def validate(prov_document):
    provjson = prov_document.get_provjson()

    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}

    try:
        req = urllib2.Request(URL_VALIDATOR_SERVICE, provjson, headers)
        response = urllib2.urlopen(req)

        graph_url = response.geturl()
        validation_url = re.sub('.json', '', graph_url) + '/validation/report'

        req = urllib2.Request(validation_url, None, {'Accept': 'application/xml'})
        response = urllib2.urlopen(req)

        xml_report = response.read()

        matches = set(re.findall('(?<=<ns2:)\w+', xml_report))
        nonfails = set(['validationReport', 'success', 'successfulMerge', 'deposited'])

        result = matches - nonfails

        valid = len(result) == 0

        return valid, validation_url

    except Exception, e:
        if DEBUG or TESTRUN:
            traceback.print_exc()
            print e
        logger.warn('Could not access the validation service.')


def convert_path(path, recursive=False):
    if os.path.isdir(path):
        for child in os.listdir(path):
            child_path = os.path.join(path, child)
            if recursive and os.path.isdir(child_path):
                convert_path(child_path, recursive)
            elif os.path.isfile(child_path):
                convert_graphml_file(child_path)
    elif os.path.isfile(path):
        convert_graphml_file(path)


@logging_intercept
def convert_xml_root(root):
    c = GraphMLProvConverter(root)
    return c.prov


def convert_graphml_string(content):
    root = etree.fromstring(content)
    return convert_xml_root(root)


def convert_graphml_file(filepath):
    root, ext = os.path.splitext(filepath)
    if ext == '.graphml':
        logger.info('Converting file %s...' % filepath)
        tree = etree.parse(filepath)
        prov_doc = convert_xml_root(tree.getroot())
        with codecs.open(root + '.provn', 'w', encoding='utf-8') as f:
            logger.debug('Writing to %s.provn' % root)
            provn = prov_doc.get_provn()
            f.write(provn)
        with codecs.open(root + '.json', 'w', encoding='utf-8') as f:
            logger.debug('Writing to %s.json' % root)
            provjson = prov_doc.get_provjson(indent=2)
            f.write(provjson)
        valid, validation_url = validate(prov_doc)
        if valid:
            logger.info('The output PROV document is valid.')
        else:
            logger.warn('The output PROV document is INVALID. Please check the validation report at %s' % validation_url)


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Trung Dong Huynh on %s.
  Copyright 2013 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE")
        parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')

        # Process arguments
        args = parser.parse_args()

        paths = args.paths
        verbose = args.verbose
        recurse = args.recurse
        inpat = args.include
        expat = args.exclude

        if verbose > 0:
            print("Verbose mode on")
            if recurse:
                print("Recursive mode on")
            else:
                print("Recursive mode off")

        if inpat and expat and inpat == expat:
            raise CLIError("include and exclude pattern are equal! Nothing will be processed.")

        for inpath in paths:
            convert_path(inpath, recurse)

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            traceback.print_exc()
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    logging.basicConfig(level=(logging.DEBUG if DEBUG else logging.INFO))
    if DEBUG:
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'converter_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
