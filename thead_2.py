import threading
import time
import serial
from PROYECTO_2_1 import read_mpu6050_data  # Importa la función del sensor desde el archivo PROYECTO_2_1.py

# Variables globales
window_size = 10  # Valor por defecto para N
ser = None  # Variable para el puerto serial

# Función para escribir en el puerto serial
def write_to_serial():
    global ser
    while True:
        # Calcula el promedio de las últimas N lecturas y almacénalo en "average".
        data = read_mpu6050_data()  # Lee datos del sensor en el formato "Gx=%.2f Gy=%.2f Gz=%.2f"
        Gx, Gy, Gz = parse_sensor_data(data)
        average = calculate_average(Gx, Gy, Gz, window_size)

        # Escribe el promedio en el puerto serial.
        if ser:
            ser.write("##PROMEDIO-{}-##\n".format(average).encode('utf-8'))
        
        time.sleep(1)  # Ajusta la frecuencia de envío según tus necesidades.

# Función para leer desde el puerto serial
def read_from_serial():
    global ser, window_size
    while True:
        line = ser.readline().decode('utf-8')
        
        # Verifica si la línea leída es un comando de configuración.
        if line.startswith("##CONFIG-") and line.endswith("-##\n"):
            parts = line.strip().split("-")
            if len(parts) == 3:
                command = parts[1]
                value = parts[2]
                if command == "N":
                    try:
                        window_size = int(value)
                        print("Tamaño de la ventana configurado a", window_size)
                    except ValueError:
                        print("Valor de N inválido:", value)

# Función para configurar el tamaño de la ventana de promedio a través del puerto serial
def configure_window_size():
    global ser
    while True:
        cmd = input("Ingrese el nuevo valor de N: ")
        if ser:
            ser.write("##CONFIG-N-{}-##\n".format(cmd).encode('utf-8'))

def parse_sensor_data(data):
    # Supongamos que puedes analizar los datos del sensor en el formato proporcionado.
    parts = data.split()
    Gx = float(parts[0][3:])
    Gy = float(parts[2][3:])
    Gz = float(parts[4][3:])
    return Gx, Gy, Gz

def calculate_average(Gx, Gy, Gz, N):
    # Supongamos que tienes una función que calcula el promedio de las últimas N lecturas.
    # Puedes implementar aquí tu lógica de cálculo de promedio.
    return (Gx + Gy + Gz) / N

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB0', 115200)  # Ajusta el puerto y velocidad según tu configuración

    mpu_thread = threading.Thread(target=read_mpu6050_data)
    serial_write_thread = threading.Thread(target=write_to_serial)
    serial_read_thread = threading.Thread(target=read_from_serial)
    config_thread = threading.Thread(target=configure_window_size)

    mpu_thread.start()
    serial_write_thread.start()
    serial_read_thread.start()
    config_thread.start()

    mpu_thread.join()
    serial_write_thread.join()
    serial_read_thread.join()
    config_thread.join()
