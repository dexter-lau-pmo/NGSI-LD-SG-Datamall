import mylibs.constants  as constants
import mylibs.ngsi_ld  as ngsi_ld
from landtransportsg import Traffic
import requests
import urllib.parse

import json
from requests.exceptions import RequestException, HTTPError
from ngsildclient import Client, Entity, SmartDataModels
from datetime import datetime, timezone


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
    current_time_utc = datetime.now(timezone.utc)
    
    #Import data from LTA
    LTA_client = Traffic(API_KEY)
    carpark_list = LTA_client.carpark_availability()

    print("Example Carpark: ",carpark_list[0])
    print("Number of carparks: ", len(carpark_list))
    

    for carpark in carpark_list:
    
        #Skip loop if entry is not about cars
        if carpark["LotType"] != "C":
            continue
    
        remove_spaced_name = carpark["Development"].replace(' ', '') #remove spaces in development name
        id = remove_spaced_name + str(carpark["CarParkID"])  #carparkID would be developmentname plus ID?
        print("ID: ", id)
        entity = Entity("Carpark", id , ctx=ctx) #type, id , ctx
        #entity.tprop("observedAt", time_now) #Append time that lot was created to be now
        
        for key, value in carpark.items():
            if key == "CarParkID":
                entity.prop("CarParkID", value)
            elif key == "Area":
                entity.prop("Region", value)
            elif key == "Development":
                entity.prop("DevelopmentName", value)
            elif key == "Location": # Geoproperty
                geocoordinates = value.split() #lat, long
                if len(geocoordinates) > 1:
                    entity.gprop("location", ( float(geocoordinates[0]) , float(geocoordinates[1]) ) ) #Pass in point
                    print("Lat " , geocoordinates[0] , " Long " , geocoordinates[1])
            elif key == "AvailableLots":
                entity.prop("ParkingAvalibility", value, observedat=current_time_utc)
            elif key == "LotType":
                entity.prop("LotType", value)
            elif key == "Agency":
                entity.rel("ParkingSiteOwner", value)
                
        entity_list.append(entity) # Add entity to list
            
            
    return entity_list


def retrieve_carparks():
    return ngsi_ld.retrieve_ngsi_type("Carpark")



#Moved to ngsi_ld.py
'''                
def create_entities_in_broker (entities):
    with Client(hostname=broker_url, port=broker_port, tenant=broker_tenant, port_temporal=temporal_port ) as client:
        count = 0
        for entity in entities:
            ret = client.upsert(entity)
            if ret:
                count +=1
    print("Uploaded ", count)
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
    

def retrieve_entity_from_json_file(output_file=constants.cache):
    entity_list: list[Entity] = Entity.load(output_file)
    print("\n\n")
    #print(carpark_list)
    print("Number of entities received:  " , len(entity_list))
    return entity_list

def retrieve_entity_from_json_file(output_file=constants.cache):
    try:
        entity_list = Entity.load(output_file)
    except Exception as e:
        print(f"Failed to load entities from {output_file}: {e}")
        return []

    print("\n\n")
    print("Number of entities received:", len(entity_list))
    return entity_list


def geoquery_ngsi_long(input_type: str, geoquery: str, broker_url=broker_url, broker_tenant=broker_tenant, ctx=ctx):

    url = f"http://{broker_url}/api/broker/ngsi-ld/v1/entities/?type={input_type}&{geoquery}"

    payload = {}
    headers = {
        'NGSILD-Tenant': broker_tenant,
        'fiware-servicepath': '/',
        'Link': f'<{ctx}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    
        # Save the response to a file as a JSON array
    try:
        data = json.loads(response.text)
        if not isinstance(data, list):
            data = [data]
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Response saved to {output_file}")
    except json.JSONDecodeError as e:
        print("Failed to parse JSON response:", e)
        print("Response text:", response.text)
    
    return retrieve_entity_from_json_file(output_file)

#Documentation
#https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.01.01_60/gs_cim009v010101p.pdf
#4.10 NGSI-LD Geo-query language
def geoquery_ngsi_point(input_type: str , maxDistance: int, lat: float, long: float , output_file=constants.cache , broker_url=broker_url, broker_tenant=broker_tenant, ctx=ctx):
    
    geometry="Point"
    
    # URL encode the coordinates
    #encoded_coordinates = urllib.parse.quote(f"[{lat},{long}]")
    encoded_coordinates = urllib.parse.quote(f"[{long},{lat}]")

    # Construct the geoquery string
    georel = f"near%3BmaxDistance=={maxDistance}"
    geoquery = f"geometry={geometry}&georel={georel}&coordinates={encoded_coordinates}"

    # Construct the full URL
    url = f"http://{broker_url}/api/broker/ngsi-ld/v1/entities/?type={input_type}&{geoquery}"

    payload = {}
    headers = {
        'NGSILD-Tenant': broker_tenant,
        'fiware-servicepath': '/',
        'Link': f'<{ctx}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
    }

    print(url)
    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    
        # Save the response to a file as a JSON array
    try:
        data = json.loads(response.text)
        if not isinstance(data, list):
            data = [data]
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Response saved to {output_file}")
    except json.JSONDecodeError as e:
        print("Failed to parse JSON response:", e)
        print("Response text:", response.text)
    
    return retrieve_entity_from_json_file(output_file)

            
def delete_all_type(type):
    with Client(hostname=broker_url, port=broker_port, tenant=broker_tenant, port_temporal=temporal_port ) as client:
        entities = client.query(type=type, ctx=ctx)
        print("Entities retrieved: ", len(entities))

        #Delete by type
        #client.drop("https://schema.org/BusStop")

        #Delete by list
        client.delete(entities)

'''
           