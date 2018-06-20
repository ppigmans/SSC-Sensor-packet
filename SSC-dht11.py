# Author 		= 	"Patrick Pigmans"
# Copyright Company	= 	"Shared Service Center"
# Copyright Author	=	"Patrick Pigmans"
# Company address	=	"Edisonweg 4A, Vlissingen, The Netherlands"
# License	 	= 	"Public Domain"
# Version 		= 	"1.0"

import os
import time
import sys
import Adafruit_DHT as dht
import paho.mqtt.client as mqtt
import json

# host = ip van server
# user = gebruikersnaam gekoppeled aan de MQTT node van node-red

host = '192.168.11.21'
user = 'test'

# hier wordt aangegeven om de hoeveel seconden de code opnieuw moet uitgevoert worden

INTERVAL=2

#hoe de data wordt verzonden, in dit geval puur het getal.
sensor_temp = {0}
sensor_hum = {0}

next_reading = time.time() 

# als het woord client wordt gebruikt wordt mqtt.client() opgeroepen

client = mqtt.Client()

# welke gebruikersnaam wordt er gebruikt, in dit geval is het een referencie terug naar "user"
client.username_pw_set(user)
# maak een MQTT verbinding naar 'host' die eerder staat aangegeven in de code, het maakt gebruikt van de standaard mqtt port: 1883, deze verbinding blijf 60 seconden bestaan.
client.connect(host, 1883, 60)

#Vanaf hier gaat de code verzonden in een loop.

client.loop_start()

try:
    while True:
        humidity,temperature = dht.read_retry(dht.DHT11, 4)
        humidity = round(humidity, 2)
        temperature = round(temperature, 2)
        print(u"Temperatuur: {:g}\u00b0C, Luchtvochtigheid: {:g}%".format(temperature, humidity))
        sensor_temp = temperature
        sensor_hum = humidity

        # Sending humidity and temperature data to ThingsBoard
        client.publish('lv', json.dumps(sensor_hum), 1)
		client.publish('temp', json.dumps(sensor_temp), 1)

        next_reading += INTERVAL
        sleep_time = next_reading-time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()
