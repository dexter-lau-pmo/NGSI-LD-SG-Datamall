

# NGSI-LD Datamall

## Readme

### Step 1: Create Virtual Environment

- **On Windows:**
  ```bash
  python -m venv myenv
  ```

### Step 2: Activate Virtual Environment

- **On Windows:**
  ```bash
  myenv\Scripts\activate
  ```

- **On macOS/Linux:**
  ```bash
  source myenv/bin/activate
  ```

### Step 3: Install Libraries

```bash
pip install landtransportsg
pip install ngsildclient
pip install geopy
```

### Step 4: Start NGSI-LD Broker

Run a local copy of the NGSI-LD Broker. Refer to the broker's documentation for setup instructions.

### Step 5: Run Script to Import NGSI-LD Entities

```bash
python import_parkingspots.py
```

### Step 6: Start Telegram Bot

```bash
python telegram_bot.py
```

### Step 7: Interact with the Bot

1. Open Telegram.
2. Search for **#Ljp_ngsi_bot**.
3. Send `/start` to the bot.
4. Follow the instructions provided by the bot.

## Configurations

If you are not using the default broker configurations, please update the settings in `myLibs/constants.py` accordingly.


