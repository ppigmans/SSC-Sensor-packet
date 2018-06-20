import time
import paho.mqtt.client as mqtt 
from smbus import SMBus
import json
import sys
 
bus = SMBus(1)
host = '172.16.85.250'
user = 'weather-station'
INTERVAL=2
next_reading = time.time() 
MPL115A2_ADDRESS = (0x60)
 
MPL115A2_REGISTER_PRESSURE_MSB  = (0x00)
MPL115A2_REGISTER_PRESSURE_LSB  = (0x01)
MPL115A2_REGISTER_TEMP_MSB      = (0x02)
MPL115A2_REGISTER_TEMP_LSB      = (0x03)
MPL115A2_REGISTER_A0_COEFF_MSB  = (0x04)
MPL115A2_REGISTER_A0_COEFF_LSB  = (0x05)
MPL115A2_REGISTER_B1_COEFF_MSB  = (0x06)
MPL115A2_REGISTER_B1_COEFF_LSB  = (0x07)
MPL115A2_REGISTER_B2_COEFF_MSB  = (0x08)
MPL115A2_REGISTER_B2_COEFF_LSB  = (0x09)
MPL115A2_REGISTER_C12_COEFF_MSB = (0x0A)
MPL115A2_REGISTER_C12_COEFF_LSB = (0x0B)
MPL115A2_REGISTER_STARTCONVERSION = (0x12)
 
 
a0_MSB = -1;
a0_LSB = -1;
b1_MSB = -1;
b1_LSB = -1;
b2_MSB = -1;
b2_LSB = -1;
c12_MSB = -1;
c12_LSB = -1;
 
client = mqtt.Client()
# welke gebruikersnaam wordt er gebruikt, in dit geval is het een referencie terug naar "user"
client.username_pw_set(user)
# maak een MQTT verbinding naar 'host' die eerder staat aangegeven in de code, het maakt gebruikt van de standaard mqtt port: 1883, deze verbinding blijf 60 seconden bestaan.
client.connect(host, 1883, 60)

pressure_MSB = -1
pressure_LSB = -1
 
temp_MSB = -1
temp_LSB = -1
 
def readCoefficients():
   global a0_MSB;
   global a0_LSB;
   global b1_MSB;
   global b1_LSB;
   global b2_MSB;
   global b2_LSB;
   global c12_MSB;
   global c12_LSB;
 
   a0_MSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_A0_COEFF_MSB+0);
   a0_LSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_A0_COEFF_LSB+0);
 
   b1_MSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_B1_COEFF_MSB+0);
   b1_LSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_B1_COEFF_LSB+0);
 
   b2_MSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_B2_COEFF_MSB+0);
   b2_LSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_B2_COEFF_LSB+0);
 
   c12_MSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_C12_COEFF_MSB+0);
   c12_LSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_C12_COEFF_LSB+0);


client.loop_start()

# MAIN
#
try:
	while True:
		readCoefficients()
 
#
# unpack to 10bits full scale
		_mpl115a2_a0 = (float)( (a0_MSB<<8) | a0_LSB  ) / (2<<3)
		_mpl115a2_b1 = (float)( (b1_MSB<<8) | b1_LSB  ) / (2<<13)
		_mpl115a2_b2 = (float)( (b2_MSB<<8) | b2_LSB  ) / (2<<14)
		_mpl115a2_c12 = (float)( (c12_MSB<<8) | (c12_LSB >>2) ) / (2<<13)
 
#
# send conversion command   
		bus.write_i2c_block_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_STARTCONVERSION,[0x12])
 
#   
# sleep until the conversion is certainly completed
		time.sleep(0.5);
 
#
# pressure AGC units
		pressure_MSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_PRESSURE_MSB);
		pressure_LSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_PRESSURE_LSB);
 
#
# temperatture AGC units
		temp_MSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_TEMP_MSB+0);
		temp_LSB = bus.read_byte_data(MPL115A2_ADDRESS,MPL115A2_REGISTER_TEMP_LSB+0);
 
		pressure = (pressure_MSB<< 8 | pressure_LSB) >>6;
 
		temperature = (temp_MSB<<8 | temp_LSB) >>6;
 
		pressureComp = _mpl115a2_a0 + (_mpl115a2_b1 + _mpl115a2_c12 * temperature ) * pressure + _mpl115a2_b2 * temperature;
 
#
# Return pressure and temperature as floating point values
# P = Pascall, terwijl als je het deelt door 10 (P/10) het veranderd naar Hectopascall. wat makkleijker leesbaar is
		P = ((65.0 / 1023.0) * pressureComp) + 50.0; 
 		LD = round(P/10000, 2)
		print "%.2f BAR" % (P/10000)
		client.publish('WS/ld', json.dumps(LD), 1)

        next_reading += INTERVAL
        sleep_time = next_reading-time.time()
        if sleep_time > 0:
				time.sleep(sleep_time)
except KeyboardInterrupt:
    pass
client.loop_stop()
client.disconnect()
