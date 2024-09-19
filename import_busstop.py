import sys 
print(sys.version)

#LTA

import mylibs.constants  as constants
import mylibs.ngsi_ld  as ngsi_ld
from landtransportsg import PublicTransport

import json
from requests.exceptions import RequestException, HTTPError
from ngsildclient import Client, Entity, SmartDataModels
from datetime import datetime


API_KEY = constants.LTA_API_KEY

lta_client = PublicTransport(API_KEY)
bus_stop_list = lta_client.bus_stops()
print("Number of Bus stops is: " , len(bus_stop_list))
print("Example bus stop: " , bus_stop_list[0])


#NGSI-LD



# No context provided => defaults to NGSI-LD Core Context
#ctx = "http://34.126.76.13/context.jsonld"
ctx = constants.ctx
broker_url = constants.broker_url
broker_port = constants.broker_port # default, 80
temporal_port = constants.temporal_port #default 1026
broker_tenant = constants.broker_tenant


#Context: https://schema.org/BusStop
#API: https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf
#JSOn-LD visualiser: https://json-ld.org/playground/

#import data from LTA

print("\n\n\nGet bus stops from LTA\n")
count = 0
for bus_stop in bus_stop_list:
    print("BusStopCode is: " , bus_stop['BusStopCode'])
    id = "BusStop" + bus_stop['BusStopCode'] #Create NGSI-LD ID from the BusStopCode. All other params can be directly loaded
    bus_stop['id'] = id
    print("Calculated NGSI-LD ID should be: " , bus_stop['id'])

    #Create Geoproperty dictionary
    d = {}
    d['location'] = {}
    d['location']['type'] = "GeoProperty"
    d['location']['value'] = {}
    d['location']['value']['type'] = "Point"
    d['location']['value']['coordinates'] = [ bus_stop['Longitude'] , bus_stop['Latitude'] ]
    bus_stop['location'] = d['location'] # Add Geoproperty to dict
    
    
    print("Calculated NGSI-LD Geolocation should be: " , bus_stop['location'])

print(bus_stop_list[0])



print("\n\n\n\n\n\n_______________________________________\n\n\n")
print("Format data in NGSI-LD")

#Create entity locally only

entity_list = []
count = 0

for bus_stop in bus_stop_list:
    print(bus_stop.keys())
    print(bus_stop['id'])
    entity = Entity("BusStop", bus_stop['id'], ctx=ctx) #Entity type, id
    
    # gprop() sets a GeoProperty : Point, Polygon, ...
    entity.gprop("location", (bus_stop['Latitude'], bus_stop['Longitude']))

    for key, value in bus_stop.items():
        if key!='location' and key!='id':
            entity.prop(key, value)
    
    entity_list.append(entity) #Add to list
    # rel() sets a Relationship Property
    
    
entity.pprint()

print("Attempt to upload to broker")

#Put entity in broker

ngsi_ld.create_entities_in_broker(entity_list, batch_size=100)
