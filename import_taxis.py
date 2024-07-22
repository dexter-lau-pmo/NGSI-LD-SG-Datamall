
from landtransportsg import PublicTransport
API_KEY = "kcrIN/xHRrOPV3EqD/+i+A=="

lta_client = PublicTransport(API_KEY)
taxi_list = lta_client.taxi_availability()
print("Number of Bus stops is: " , len(taxi_list))
print("Example bus stop: " , taxi_list[0])

import json
from requests.exceptions import RequestException, HTTPError
from ngsildclient import Client, Entity, SmartDataModels
from datetime import datetime

print("Taxi list")
print(taxi_list)
    
    
