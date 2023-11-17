#Original Code by Thingsboard Team
#Modified by juan
import os
import time
import sys
import board
import paho.mqtt.client as mqtt

import json
THINGSBOARD_HOST = 'thingsboard.cloud'
ACCESS_TOKEN = 'M5YnmYBoPFgJHPr0npGN'
import smbus					#import SMBus module of I2C

from time import sleep          #import

from w1thermsensor import W1ThermSensor #Importamos el paquete W1ThermSensor

sensor = W1ThermSensor() #Creamos el objeto sensor


# MPU6050 registro 
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)

client.loop_start()
sensor_data = {'Ax': 0, 'Ay': 0, 'Ax': 0, 'Temp': 0}


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	 bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

print ("Data de mcp 6050")
try:
    while True:
        
        #Read Accelerometer raw value
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)
        
        #Read Gyroscope raw value
        #gyro_x = read_raw_data(GYRO_XOUT_H)
        #gyro_y = read_raw_data(GYRO_YOUT_H)
        #gyro_z = read_raw_data(GYRO_ZOUT_H)
        
        #Full scale range +/- 250 degree/C as per sensitivity scale factor
        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0
        
        #Gx = gyro_x/131.0
        #Gy = gyro_y/131.0
        #Gz = gyro_z/131.0
        #sum =sqrt(Gx*Gx+Gy*Gy+Gz*Gz)
        #sum2 =sqrt(Ax*Ax+Ay*Ay+Az*Az)
        

        print (Ax)
        #print (sum)
        #print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s") 	
        #print (sum2)
        #print ("ax=%.2f" %Ax, u'\u00b0'+ "/s", "\tay=%.2f" %Ay, u'\u00b0'+ "/s", "\taz=%.2f" %Az, u'\u00b0'+ "/s") 	
        print ("ax=%.2f" %Ax, "\tay=%.2f" %Ay, "\taz=%.2f" %Az) 	
        
        sleep(0.1)
        #system("clear")
        temperature = sensor.get_temperature()                #Obtenemos la temperatura en centígrados
        print("Temp %s " % temperature)  #Imprimimos el resultado
                                            #Esperamos un segundo antes de terminar el ciclo 


        
        sensor_data['Ax'] = Ax
        sensor_data['Ay'] = Ay
        sensor_data['Az'] = Az
        sensor_data['Temp'] = temperature

            # Sending humidity and temperature data to ThingsBoard
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()
	
