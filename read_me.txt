cd /d D:\GitHub\ngsi-ld-python\NGSI-LD-SG-Datamall

To run:
python -m venv myenv (create venv, skip step if done previously)
myenv\Scripts\activate
python import_parkingspots.py




Headers:  {'Link': '<[\'http://34.126.76.13/context.jsonld\']>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'}
Count wraps the link wrongly => Replace context as string instead of list of strings

api/broker/ngsi-ld/v1/entities/?type=Carpark&geometry=Point&georel=near%3BmaxDistance==800&coordinates=%5B103.83359,1.3071%5D
api/broker/ngsi-ld/v1/entities/?type=Carpark&geometry=Point&georel=near%3BmaxDistance==800&coordinates=%5B103.83359,1.3071%5D
api/broker/ngsi-ld/v1/entities/?type=Carpark&geometry=Point&georel=near%3B100==800&coordinates=%5B103.83359%2C1.3071%5D