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


entity_list = ngsi_ld.retrieve_ngsi_type("Taxi")
Entity.save_batch(entity_list , "Taxi.txt")
