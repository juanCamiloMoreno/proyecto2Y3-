import os
import time
import sys
import board
import paho.mqtt.client as mqtt
import json
import smbus
from time import sleep
from w1thermsensor import W1ThermSensor
import threading

THINGSBOARD_HOST = 'thingsboard.cloud'
ACCESS_TOKEN = 'M5YnmYBoPFgJHPr0npGN'
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()
sensor_data = {'Ax': 0, 'Ay': 0, 'Ax': 0, 'Temp': 0}


# Configuración del sensor I2C
bus = smbus.SMBus(1)
Device_Address = 0x68

# Variables para el cálculo del promedio
n = 10  # Valor predeterminado para N
readings = []

# Función para inicializar el sensor MPU6050

# Función para leer desde el sensor I2C a la tasa más alta
def read_sensor():
    while True:
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)
        
        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0
        
        temperature = sensor.get_temperature()
        
        sensor_data['Ax'] = Ax
        sensor_data['Ay'] = Ay
        sensor_data['Az'] = Az
        sensor_data['Temp'] = temperature

        # Enviar datos a ThingsBoard
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)
        sleep(0.01)  # Ejemplo de pausa para una alta tasa de lectura

# Función para calcular y escribir el promedio en el puerto serial
def write_average():
    global n, readings
    with serial.Serial('/dev/ttyUSB0', 115200) as ser:  # Reemplaza '/dev/ttyUSB0' por tu puerto serial
        while True:
            if len(readings) >= n:
                average = sum(readings[-n:]) / n
                ser.write(f"##PROMEDIO-{n:03d}-{average:.2f}##\n".encode())
            time.sleep(1)

# Función para leer desde el puerto serial
def read_serial():
    with serial.Serial('/dev/ttyUSB0', 115200) as ser:  # Reemplaza '/dev/ttyUSB1' por tu puerto serial
        while True:
            line = ser.readline().decode().strip()
            match = re.match(r"##PROMEDIO-(\d+)-([\d.]+)##", line)
            if match:
                n = int(match.group(1))
                average = float(match.group(2))
                print(f"Ventana de promedio: {n}, Promedio: {average}")
            else:
                print("Mensaje no válido: ", line)

# Inicializar el sensor y otros componentes
sensor = W1ThermSensor()
#MPU_Init()

# Crear y arrancar los hilos
sensor_thread = threading.Thread(target=read_sensor)
average_thread = threading.Thread(target=write_average)
serial_thread = threading.Thread(target=read_serial)

sensor_thread.start()
average_thread.start()
serial_thread.start()
