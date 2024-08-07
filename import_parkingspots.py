import mylibs.constants  as constants
from landtransportsg import Traffic
import requests
import urllib.parse

import json
from requests.exceptions import RequestException, HTTPError
from ngsildclient import Client, Entity, SmartDataModels
from datetime import datetime
import mylibs.ngsi_ld_parking as ngsi_parking
from geopy.distance import geodesic


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
                entity.prop("ParkingAvalibility", value)
            elif key == "LotType":
                entity.prop("LotType", value)
            elif key == "Agency":
                entity.prop("ParkingSiteOwner", value)
                
        entity_list.append(entity) # Add entity to list
            
        count +=1
        if count == 50000: # Limit number of carparks pulled for now
            break
            
    return entity_list

#TO optimise this
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

    
def geoquery_ngsi_point(input_type: str , maxDistance: int, lat: float, long: float , broker_url=broker_url, broker_tenant=broker_tenant, ctx=ctx):
    
    geometry="Point"
    
    # URL encode the coordinates
    encoded_coordinates = urllib.parse.quote(f"[{lat},{long}]")
    
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
    
    

                
def retrieve_carparks():
    return retrieve_ngsi_type("Carpark")
            
def delete_all_type(type):
    with Client(hostname=broker_url, port=broker_port, tenant=broker_tenant, port_temporal=temporal_port ) as client:
        entities = client.query(type=type, ctx=ctx)
        print("Entities retrieved: ", len(entities))

        #Delete by type
        #client.drop("https://schema.org/BusStop")

        #Delete by list
        client.delete(entities)


            
'''
entity_list = get_parking_data()
print ("Num entities to upload" , len(entity_list))
entity_list[1].pprint()
create_entities_in_broker(entity_list)


print("\n\n\n\n\n")
retrieved_carparks = retrieve_carparks()
print ("Num entities retrieved" , len(retrieved_carparks))
retrieved_carparks[0].pprint()

'''
print("\n\n\n\n\n")
#delete_all_type("Carpark")
gq = "geometry=Point&georel=near%3BmaxDistance==800&coordinates=%5B103.83359,1.3071%5D"
#retrieved_carparks = geoquery_ngsi_long(input_type = "Carpark" , geoquery = gq)

geoquery_ngsi_point(input_type = "Carpark", maxDistance=10000 , lat = 103.83349, long= 1.3072)

nearest_carparks = ngsi_parking.geoquery_ngsi_point(input_type = "Carpark", maxDistance=1000 , long = 103.83349, lat= 1.3072)

print(nearest_carparks)


closest_three_carparks = []
for carpark in nearest_carparks:
    carpark_dict = carpark.to_dict()
    
    print(carpark_dict["location"])
    print(carpark_dict["location"]["value"]["coordinates"])
    lat = carpark_dict["location"]["value"]["coordinates"][1]
    long = carpark_dict["location"]["value"]["coordinates"][0]
    print(carpark_dict["location"]["value"]["coordinates"][0])
    print(carpark_dict["location"]["value"]["coordinates"][1])
    distance = geodesic((1.3072, 103.83349), (lat, long)).km
    carpark["distance"] = distance
    print(
        "\nArea: " + str(carpark_dict["DevelopmentName"]["value"]) + " \nLots: " + str(carpark_dict["ParkingAvalibility"]["value"]) + "\n Distance from destination is:  " + str(distance) + "km"
    )
    print(carpark_dict["LotType"]["value"])
    
    #Find closest 3 carparks
    if len(closest_three_carparks)<3 and carpark_dict["LotType"]["value"] == "C":
        closest_three_carparks.append(carpark)
    else:
        for closestcarpark in closest_three_carparks :
            if closestcarpark["distance"]>carpark["distance"]: #Carpark is closer than one on list
                closestcarpark = carpark
                break
                
count = 1
closest_carparks = "The closest 3 carparks to your destination are:  \n\n" 
for carpark in closest_three_carparks:
    closest_carparks = closest_carparks + "\n" + str(count) + ": " + "\nArea: " + str(carpark_dict["DevelopmentName"]["value"]) + " \nLots: " + str(carpark_dict["ParkingAvalibility"]["value"]) + "\n Distance from destination is:  " + str(distance) + "\n"
    count += 1

#Send msg to user
print(
    closest_carparks
)