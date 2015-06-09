#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from operator import itemgetter

"""reg
Based on example code from lesson 6. 

Attempt to clean up the data by lowering and underscoring amenities and correcting streets.


"""

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
city_state_re = re.compile(r'(\w+)\s+(\w+)\s+(\d+)', re.IGNORECASE)
house_number_re = re.compile(r'(\d+)\s+(.*)')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

mapping = { "st": "Street",
            "st.": "Street",
            "st..": "Street",
            "rd.": "Road",
            "rd": "Road",
            "ave": "Avenue",
            "ave.": "Avenue",
            "plz": "Plaza"
            }

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node["created"] = {}
        node["type"] = element.tag
        for att in element.keys():
            if att in CREATED:
                node["created"][att] = element.get(att)
            elif att == "lat" or att == "lon":
                continue
            else:
                node[att] = element.get(att)
            
        if element.get("lon") and element.get("lat"):
            node["pos"] = [float(element.get("lat")), float(element.get("lon"))]
        
        address = {}
        for t in element.iter("tag"):
   
            k_val = t.get("k")
            v_val = t.get("v")

            if k_val == "amenity":
                node["amenity"] = shape_amenity(v_val)
            elif k_val == "address":
                address = shape_non_karlsruhe(v_val)
            else:
                reg0 = problemchars.search(k_val)
                reg1 = lower.search(k_val)
                if reg0:
                    continue
                    
                reg2 = lower_colon.search(k_val)
                if reg2:
                    # get address
                    tokenized = reg2.group().split(":")
                    if tokenized[0] != "addr":
                        continue
                    res = tokenized[-1]
                    if res == "street":
                        street_type_match = street_type_re.search(v_val)
                        if street_type_match:
                            street_type = street_type_match.group()
                            if street_type.lower() in mapping:
                                address[res] = replace_words(v_val, {street_type: mapping[street_type.lower()]})
                            else:
                                address[res] = v_val
                        else:
                            address[res] = v_val
                    else:
                        address[res] = v_val
                else:
                    node[k_val] = v_val 
                
        if len(address) > 0:
            node["address"] = address
        
        node_refs = []
        for t in element.iter("nd"):
            node_refs.append(t.get("ref"))
        
        if len(node_refs) > 0:
            node["node_refs"] = node_refs
        return node
    else:
        return None

# Shape amenity
def shape_amenity(amenity):
    return amenity.lower().replace(" ", "_")

# Shape non karlsruhe type address
def shape_non_karlsruhe(address):
    # pick up the street
    new_address = {}
    tokenized_addr = address.split(",")
    if len(tokenized_addr) > 1:
        addr = tokenized_addr[0].strip()
        street_type_match_result = street_type_re.search(addr)
        if street_type_match_result:
            street_type = street_type_match_result.group()
            new_addr = ""
            if street_type.lower() in mapping:
                new_addr = replace_words(addr, {street_type: mapping[street_type.lower()]})

            else:
                new_addr = replace_words(addr)

            house_number_match = house_number_re.match(new_addr)
            if house_number_match:
                new_address["street"] = house_number_match.group(2)
                new_address["housenumber"] = house_number_match.group(1)
            else:
                new_address["street"] = new_addr

        # Get the city, state and postal code
        city_state = tokenized_addr[-1].strip()
        city_state_match = city_state_re.search(city_state)
        if city_state_match:
            new_address["city"] = city_state_match.group(1)
            new_address["state"] = city_state_match.group(2)
            new_address["postcode"] = city_state_match.group(3)

    else:
        # Just keep as is
        new_address["UNKNOWN"] = replace_words(address)

    return new_address

def replace_words(word, replacement={}):
    for w in replacement:
        if replacement[w] != None:
            word = word.replace(w, replacement[w])
        else:
            print("Nothing to replace..." + w)
    return word

def create_file(filename):
    f = open(filename, 'w')
    return f

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []

    count = 0
    idx = 0
    #with codecs.open(file_out, "w") as fo:
    f = create_file(file_out + str(idx))    
    for _, element in ET.iterparse(file_in):
        el = shape_element(element)
        if el:
            if count % 400 == 0:
                # open new file
                f.close()
                idx+=1
                print("...new file: ", idx)
                f = create_file(file_out + str(idx))

            data.append(el)
            if pretty:
                f.write(json.dumps(el, indent=2)+"\n")
            else:
                f.write(json.dumps(el) + "\n")

            count+=1
    
    f.close()

    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('data/boston_massachusetts_small.osm', False)
    #pprint.pprint(data)
    

if __name__ == "__main__":
    test()