#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from operator import itemgetter

"""
Based on example code from lesson 6. 

Audit the data.

"""

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

mapping = { "St": "Street",
            "St.": "Street",
            "Rd.": "Road",
            "Ave": "Avenue"
            }

def audit(file_in):
    data = {}
    # amenities = set([])
    amenities = {}
    address_types = {"non-Karlsruhe": [], "Karlsruhe": []}
    karlsruhe_streets = {"UNKNOWN": []}
    non_karlsruhe_streets = {"UNKNOWN": []}
    for _, element in ET.iterparse(file_in):
        if element.tag == "node" or element.tag == "way":            
            for atag in element.iter("tag"):
                kval = atag.get("k")
                vval = atag.get("v")

                if kval == "amenity":
                    if vval in amenities:
                        amenities[vval] += 1
                    else:
                        amenities[vval]  = 1

                if kval == "address":
                    address_types["non-Karlsruhe"].append(vval)
                    # pick up the street
                    tokenized_addr = vval.split(",")
                    if len(tokenized_addr) > 0:
                        addr = tokenized_addr[0]
                        street_type_match_result = street_type_re.search(addr)
                        if street_type_match_result:
                            street_type = street_type_match_result.group()
                            if street_type not in expected:
                                if street_type in non_karlsruhe_streets:                                
                                    non_karlsruhe_streets[street_type].append(vval)
                                else:
                                    non_karlsruhe_streets[street_type] = [vval]
                    else:
                        # Just keep as is
                        non_karlsruhe_streets["UNKNOWN"].append(vval)
                else:
                    m = lower_colon.search(kval)
                    if m:
                        tokenized_addr = kval.split(":")
                        if tokenized_addr[0] == "addr":
                            address_types["Karlsruhe"].append(vval)

                            if tokenized_addr[1] == "street":
                                # pick up the street
                                street_type_match_result = street_type_re.search(vval)
                                if street_type_match_result:
                                    street_type = street_type_match_result.group()
                                    if street_type not in expected:
                                        if street_type in karlsruhe_streets:                                        
                                            karlsruhe_streets[street_type].append(vval)
                                        else:
                                            karlsruhe_streets[street_type] = [vval]
                                else:
                                    karlsruhe_streets["UNKNOWN"].append(vval)



    return [data, amenities, address_types, non_karlsruhe_streets, karlsruhe_streets]


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []

    [data, amenities, address_types, non_karlsruhe_streets, karlsruhe_streets] = audit(file_in)


    # Sort amenities by value and print it
    sorted_amenities_pairs = sorted(amenities, key=amenities.get)
    for x in sorted_amenities_pairs:
        print(" " + x  + " => ", amenities[x])

    # with codecs.open(file_out, "w") as fo:
    #     for _, element in ET.iterparse(file_in):
    #         el = shape_element(element)
    #         if el:
    #             data.append(el)
    #             if pretty:
    #                 fo.write(json.dumps(el, indent=2)+"\n")
    #             else:
    #                 fo.write(json.dumps(el) + "\n")

    print("=> Address types")
    print(" non-Karlsruhe: ", len(address_types["non-Karlsruhe"]))
    print(" Karlsruhe: ", len(address_types["Karlsruhe"]))

    print("=> Karlsruhe Street types")
    for street_type in karlsruhe_streets:
        print(" street: ", street_type)

    #pprint.pprint(karlsruhe_streets)

    print("=> non-Karlsruhe Street types")
    for street_type in non_karlsruhe_streets:
        print(" street: ", street_type)

    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    # data = process_map('data/boston_massachusetts.osm', True)
    data = process_map('data/boston_massachusetts_small.osm', True)
    
    #pprint.pprint(data)
    
 

if __name__ == "__main__":
    test()