# NGSI-LD-SG-Datamall
 Pull open Singapore data into NGSI-LD broker

#To run
create /mylibs/constants.py
Copy /mylibs/constants.py.example into /mylibs/constants.py
Fill in your API keys

#Create venev
If necessary, create virtual environment:

```
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

#To run:
python file_name


#Quick start

Run NGSI-LD broker locally

Create carparks
```
python import_parkingspots.py
```

Use postman to query carparks

Test out different queries

Delete carparks
```
python delete_parkingspots.py
```

