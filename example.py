from datetime import datetime
from ngsildclient import Entity, Client

PARKING_CONTEXT = "https://raw.githubusercontent.com/smart-data-models/dataModel.Parking/master/context.jsonld"

e = Entity("OffStreetParking", "Downtown1")
e.ctx.append(PARKING_CONTEXT)
e.prop("name", "Downtown One")
e.prop("availableSpotNumber", 121, observedat=datetime(2022, 10, 25, 8)).anchor()
e.prop("reliability", 0.7).rel("providedBy", "Camera:C1").unanchor()
e.prop("totalSpotNumber", 200).loc(41.2, -8.5)

print("NGSI-LD Entity")
e.pprint()
print("\n")

broker_url = "localhost"
broker_port = 80 # default
broker_tenant = "openiot"

client = Client(hostname=broker_url, port=broker_port, tenant=broker_tenant)
client.create(e)






