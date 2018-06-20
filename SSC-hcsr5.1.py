import RPi.GPIO as gpio
import time
import paho.mqtt.client as mqtt
import json

gpio.setmode(gpio.BOARD)
spin1 = 7
spin2 = 11
gpio.setup(spin1, gpio.IN)
gpio.setup(spin2, gpio.IN)
host = '172.16.85.250'
user = 'weather-station'
msensor_1 = {0}
msensor_2 = {0}
next_reading = time.time()

INTERVAL=2

client = mqtt.Client()
client.username_pw_set(user)
client.connect(host, 1883, 60)

client.loop_start()

try: 
  while True:
     if gpio.input(spin1):
        print "Beweging waargenomen, Sensor 1!"
	msensor_1 = 1
	client.publish('WS/ms1', json.dumps(msensor_1), 1)
        time.sleep(2)
        
        next_reading += INTERVAL
        sleep_time = next_reading-time.time()
        if sleep_time > 0:
           time.sleep(sleep_time)
     client.loop_stop()
     client.disconnect()
except KeyboardInterrupt:
   pass
