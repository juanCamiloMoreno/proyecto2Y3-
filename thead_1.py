import threading
import time
import serial
from PROYECTO_2_1 import read_mpu6050_data  # Importa la función del sensor desde el archivo PROYECTO_2_1.py

# Define una variable global para almacenar el tamaño de la ventana de promedio
window_size = 10  # Puedes cambiar el valor por defecto según tus necesidades

# Función para escribir en el puerto serial
def write_to_serial(ser):
    while True:
        # Calcula el promedio de las últimas N lecturas y almacénalo en "average".
        # Supongamos que tienes una función que calcula el promedio.
        average = calculate_average(window_size)

        # Escribe el promedio en el puerto serial.
        ser.write("##PROMEDIO-{}-##\n".format(average).encode('utf-8'))
        
        time.sleep(1)  # Ajusta la frecuencia de envío según tus necesidades.

# Función para leer desde el puerto serial
def read_from_serial(ser):
    while True:
        line = ser.readline().decode('utf-8')
        
        # Verifica si la línea leída es válida.
        if line.startswith("##PROMEDIO-") and line.endswith("-##\n"):
            parts = line.strip().split("-")
            NNN = int(parts[1])
            # Procesa el valor de NNN según tus necesidades.
            print("Valor de NNN:", NNN)

# Función para configurar el tamaño de la ventana de promedio
def set_window_size():
    global window_size
    try:
        window_size = int(input("Ingresa el tamaño de la ventana de promedio: "))
    except ValueError:
        print("Entrada inválida. Se mantendrá el valor actual.")

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB0', 115200)  # Ajusta el puerto y velocidad según tu configuración

    mpu_thread = threading.Thread(target=read_mpu6050_data)
    serial_write_thread = threading.Thread(target=write_to_serial, args=(ser,))
    serial_read_thread = threading.Thread(target=read_from_serial, args=(ser))

    mpu_thread.start()
    serial_write_thread.start()
    serial_read_thread.start()

    # Puedes agregar un hilo adicional para configurar el tamaño de la ventana de promedio
    config_thread = threading.Thread(target=set_window_size)
    config_thread.start()

    mpu_thread.join()
    serial_write_thread.join()
    serial_read_thread.join()
    config_thread.join()
