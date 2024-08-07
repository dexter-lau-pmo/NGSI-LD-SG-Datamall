# NGSI-LD-SG-Datamall
 Pull open Singapore data into NGSI-LD broker

Step 1: Create python virtual env
python -m venv myenv

Step 2: Activate virtual env
myenv\Scripts\activate

Step 3: Install libaries
pip install landtransportsg
pip install ngsildclient
pip install geopy

Step 4: Start NGSI-LD Broker
Run a local copy of the NGSI-LD Broker

Step 5: Run script to import NGSI-LD Entities
python import_parkingspots.py

Step 6: Start Telegram bot
python telegram_bot.py

Step 7: Interact with Bot
Open Telegram
Search for #Ljp_ngsi_bot
send: /start to the bot
Follow instructions

Configurations
If you are not using the default broker configurations, please go to /myLibs/constants.py and adjust the constants accordingly
