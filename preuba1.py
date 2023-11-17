import os
import time
import sys
import board
import paho.mqtt.client as mqtt
import json
from queue import Queue
import smbus
from time import sleep
from w1thermsensor import W1ThermSensor
import threading

sensor = W1ThermSensor()

# Configuración de ThingsBoard
THINGSBOARD_HOST = 'thingsboard.cloud'
ACCESS_TOKEN = 'M5YnmYBoPFgJHPr0npGN'
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

# Crear colas para almacenar datos
acceleration_queue = Queue()
temperature_queue = Queue()

# Variable para ajustar la cantidad de valores a promediar
NNN = 5  # Puedes cambiar este valor según tus necesidades

# Variable global para almacenar el promedio
average_ax = 0

# Variable global para contar la cantidad de valores para el promedio
ax_count = 0

# Mutex para garantizar acceso seguro a las variables globales
mutex = threading.Lock()

# Variable para almacenar los datos del sensor
sensor_data = {'Ax': 0, 'Ay': 0, 'Az': 0, 'Temp': 0}

# MPU6050 registros
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

next_reading = time.time()

def MPU_Init():
    # Escribir al registro de tasa de muestreo
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    
    # Escribir al registro de administración de energía
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    
    # Escribir al registro de configuración
    bus.write_byte_data(Device_Address, CONFIG, 0)
    
    # Escribir al registro de configuración de giroscopio
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    
    # Escribir al registro de habilitación de interrupciones
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    # Los valores de aceleración y giroscopio son de 16 bits
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)
    
    # Concatenar los valores alto y bajo
    value = ((high << 8) | low)
    
    # Obtener el valor firmado desde el MPU6050
    if value > 32768:
        value = value - 65536
    return value

def average_ax_thread():
    global average_ax
    global ax_count

    while True:
        with mutex:
            if ax_count > 0:
                average_ax = sum(acceleration_queue.queue) / ax_count
                print("prom =%.2f",average_ax)
               
                ax_count = 0
        sleep(1)

# Iniciar hilo para calcular el promedio de Ax
average_thread = threading.Thread(target=average_ax_thread)
average_thread.daemon = True
average_thread.start()

bus = smbus.SMBus(1)
Device_Address = 0x68
MPU_Init()

print("Datos de MCP6050")
try:
    while True:
        # Leer valores de aceleración raw
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)

        # Rango completo +/- 250 grados/C según el factor de escala de sensibilidad
        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0

        print("Ax=%.2f" % Ax, "\tay=%.2f" % Ay, "\taz=%.2f" % Az)

        sleep(0.1)

        # Sistema de limpieza
        temperature = sensor.get_temperature()
        print("Temp %s " % temperature)

        # Almacenar valores en las colas
        with mutex:
            acceleration_queue.put(Ax)
            temperature_queue.put(temperature)
            ax_count += 1

        # Actualizar datos del sensor desde las colas
        with mutex:
            if not acceleration_queue.empty():
                sensor_data['Ax'] = acceleration_queue.get()
            if not temperature_queue.empty():
                sensor_data['Temp'] = temperature_queue.get()

        print("Ax=%.2f" % sensor_data['Ax'], "\tTemp=%.2f" % sensor_data['Temp'])

        # Enviar datos a ThingsBoard
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)

except KeyboardInterrupt:
    pass

# Detener el bucle de MQTT y cerrar la conexión
client.loop_stop()
client.disconnect()
