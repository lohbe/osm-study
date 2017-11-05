#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" audit.py - Audits node and way tags of a valid OSM XML file
    Args: None, see run_audit()
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re

import pprint

def audit_postcode_type(postcode_types, postcode):
    """ Process addr:postcode tag
    Args:
        postcode_types - Dictionary of keys not compliant to Singapore postcode format
        postcode - Postcode; 'v' attribute of addr:postcode
    """
    postcode_type_re = re.compile(r'^\d{6}$')

    match_result = postcode_type_re.search(postcode)
    if not match_result:
        postcode_types[postcode].add(postcode)

def clean_postcode(postcode):
    """ Cleans postcode
    Args:
        postcode - Postcode; 'v' attribute of addr:postcode
    Returns:
        Cleaned postcode
    """
    verbose = True
    pattern = re.compile(r'^\d{5,6}$') # valid codes are 5 or 6-digits

    match_result = pattern.search(postcode)
    if not match_result: # process non-compliant codes
        result = re.sub(r'[^\d]', '', postcode) # clean up malformed codes
    else: # do not process compliant codes
        return postcode

    if len(result) != 6: # if not compliant after clean up, set default postcode
        result = "000000"

    if verbose: print("original: {}, cleaned: {}".format(postcode, result))
    return result


def audit_lorong_type(lorong_types, street_name):
    """ Process addr:street tag
    Args:
        lorong_types - Dictionary of keys that are Lorong-street types
        street_name - Street name; 'v' attribute of addr:street
    """
    lorong_type_re = re.compile(r'(\blor\b)|(\blorong\b)', re.IGNORECASE)

    match_result = lorong_type_re.search(street_name)
    if match_result:
        lorong_type = match_result.group()
        lorong_types[lorong_type].add(street_name)


def clean_lorong(sname):
    """ Cleans lorong-style street names
    Args:
        sname - Street name; 'v' attribute of addr:street
    Returns:
        Cleaned street name
    """
    verbose = True

    # first find and replace Lor with Lorong
    result = re.sub(r'\bLor\b', 'Lorong', sname)
    # if sname != result: print("original: {}, cleaned: {}".format(sname, result))

    # then swap order of Lorong if applicable
    idx_l = result.find('Lorong')
    # if street name does not begin with lorong & a digit, swap lorong
    if (idx_l > 0) and (result[0] not in set('123456890')):
        newname = result[idx_l:]+ " " + result[:idx_l]
        if verbose: print("swap: {} -> {}".format(result, newname))
        return newname
    else:
        return result

def is_audit_field(elem, audit_field):
    """ Checks if the tag's k-attribute is the field to be audited """
    return elem.attrib['k'] == audit_field


def audit(osmfile, audit_field, audit_function):
    """ Audits the OSM file by:
    (1) looking at each tag in each node and way element,
    (2) run audit function if the tag's key matches the field we want to audit

    Args:
        OSM File,
        OSM Field to be audited, e.g. addr:street, or addr:postcode
        Audit function that processes the tags
    Returns:
        Dictionary of audited keys and a set of actual values that matched the keys
    """
    osm_file = open(osmfile, "r")
    audited_types = defaultdict(set)
    for _, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_audit_field(tag, audit_field):
                    audit_function(audited_types, tag.attrib['v'])

    osm_file.close()
    return audited_types


def run_audit():
    """Forms, runs and prints the audit query"""

    osmfile = "sample.osm"

    # Audit the street field for Lorong
    audit_osm_field = "addr:street"
    audit_function = audit_lorong_type

    # Uncomment below to audit the postcode field
    #audit_osm_field = "addr:postcode"
    #audit_function = audit_postcocde_type

    audit_result = audit(osmfile, audit_osm_field, audit_function)
    pprint.pprint(dict(audit_result))


if __name__ == '__main__':
    run_audit()
