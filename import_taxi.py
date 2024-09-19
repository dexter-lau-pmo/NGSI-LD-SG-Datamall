#Context: https://raw.githubusercontent.com/dexter-lau-pmo/NGSI-LD-SG-Datamall/main/context/custom_context.json?token=GHSAT0AAAAAACVEQXNKVWJNBF533JCYV6GQZU6FTSA

from landtransportsg import PublicTransport
import mylibs.constants  as constants
import mylibs.ngsi_ld_parking as ngsi_parking
import json
from requests.exceptions import RequestException, HTTPError
from ngsildclient import Client, Entity, SmartDataModels
from datetime import datetime, timezone
import mylibs.ngsi_ld  as ngsi_ld

API_KEY = constants.LTA_API_KEY


ctx = constants.ctx
broker_url = constants.broker_url
broker_port = constants.broker_port # default, 80
temporal_port = constants.temporal_port #default 1026
broker_tenant = constants.broker_tenant


lta_client = PublicTransport(API_KEY)
taxi_list = lta_client.taxi_availability()
print("Number of Taxis is: " , len(taxi_list))



print("Taxi list")
print(taxi_list)


count = 0

# Get the current time in UTC
current_time_utc = datetime.now(timezone.utc)

entity_list = []

for taxi_location in taxi_list:
    count += 1
    taxi_id = str(count)
    print("ID is: " , count)
    
    entity = Entity("Taxi", taxi_id, ctx=ctx) #Entity type, id
    
    # tprop() sets a TemporalProperty
    entity.tprop("dateObserved", current_time_utc)
    
    # gprop() sets a GeoProperty : Point, Polygon, ...
    entity.gprop("location", (taxi_location['Latitude'], taxi_location['Longitude']))
    
    entity_list.append(entity) #Add to list
    # rel() sets a Relationship Property

entity_list[0].pprint()

print("Attempt to upload to broker")

ngsi_ld.create_entities_in_broker(entity_list, 100)
