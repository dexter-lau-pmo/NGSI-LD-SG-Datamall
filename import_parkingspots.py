import mylibs.constants  as constants
from landtransportsg import Traffic

import json
from requests.exceptions import RequestException, HTTPError
from ngsildclient import Client, Entity, SmartDataModels
from datetime import datetime


API_KEY = constants.LTA_API_KEY
ctx = constants.ctx
broker_url = constants.broker_url
broker_port = constants.broker_port # default, 80
temporal_port = constants.temporal_port #default 1026
broker_tenant = constants.broker_tenant



#Convert to NGSI-LD
'''
Carpark
- id - Core context
- DevelopmentName (From LTA)
- Region (From LTA)
- Location - Gprop
- Price (Pending Terrence)
- ParkingAvalibility - From SDM 
- ParkingChargeType - From SDM (Pending Terrence)
- ParkingMaxAvalibility - From SDM (Info not avaliable)
- DataSource - From SDM
- ParkingSiteOwner (relationship) - From SDM


Example LTA data return:
            "CarParkID": "1",
            "Area": "Marina",
            "Development": "Suntec City",
            "Location": "1.29375 103.85718",
            "AvailableLots": 442,
            "LotType": "C",
            "Agency": "LTA"
'''

def get_parking_data(): #Get parking data in NGSI-LD format
    count = 0
    entity_list = []
    
    #Import data from LTA
    LTA_client = Traffic(API_KEY)
    carpark_list = LTA_client.carpark_availability()

    print("Example Carpark: ",carpark_list[0])
    print("Number of carparks: ", len(carpark_list))
    

    for carpark in carpark_list:
        remove_spaced_name = carpark["Development"].replace(' ', '') #remove spaces in development name
        id = remove_spaced_name + str(carpark["CarParkID"])  #carparkID would be developmentname plus ID?
        print("ID: ", id)
        entity = Entity("Carpark", id , ctx=ctx) #type, id , ctx
        
        for key, value in carpark.items():
            if key == "CarParkID":
                entity.prop("id", value)
            elif key == "Area":
                entity.prop("Region", value)
            elif key == "Development":
                entity.prop("DevelopmentName", value)
            elif key == "Location": # Geoproperty
                geocoordinates = value.split() #lat, long
                if len(geocoordinates) > 1:
                    entity.gprop("location", (geocoordinates[0] , geocoordinates[1]) ) #Pass in point
                    print("Lat " ,geocoordinates[0] , " Long " , geocoordinates[1])
            elif key == "AvailableLots":
                entity.prop("ParkingAvalibility", value)
            elif key == "LotType":
                entity.prop("LotType", value)
            elif key == "Agency":
                entity.prop("ParkingSiteOwner", value)
                
            entity_list.append(entity) # Add entity to list
            
            count +=1
            if count == 1:
                break
            return entity_list
                
def create_entities_in_broker (entities):
    with Client(hostname=broker_url, port=broker_port, tenant=broker_tenant, port_temporal=temporal_port ) as client:
        ret = client.create(entities)
    print("Upload ", ret)
    return ret

def update_entities_in_broker (entities):
    with Client(hostname=broker_url, port=broker_port, tenant=broker_tenant, port_temporal=temporal_port ) as client:
        ret = client.upsert(entities)
    print("Update ", ret)
    return ret
    
def retrieve_ngsi_type(input_type: str):
    with Client(hostname=broker_url, port=broker_port, tenant=broker_tenant, port_temporal=temporal_port ) as client:
        entities = client.query(type=input_type, ctx=ctx) #Query for all type of carpark
        print("Number of entities retrieved: ", len(entities))
        for entity in entities:
            print(entity.id)
    return entities

                
def retrieve_carparks():
    return retrieve_ngsi_type("Carparks")
            
                
entity_list = get_parking_data()
print ("Num entities" , len(entity_list))
entity_list[1].pprint()
print("\n\n\n\n\n")
create_entities_in_broker(entity_list)

retrieved_carparks = retrieve_carparks()
print ("Num entities retrieved" , len(retrieved_carparks))
retrieved_carparks[0].pprint()




