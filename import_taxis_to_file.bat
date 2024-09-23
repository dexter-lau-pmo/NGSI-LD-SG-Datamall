@echo off
echo Activating virtual environment...
echo call myenv\Scripts\activate

echo Running Python script...
python import_taxi.py
timeout 2
python retrieve_taxis.py

pause
