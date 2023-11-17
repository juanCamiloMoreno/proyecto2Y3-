import serial
import time

# Configura el puerto serial, ajusta el puerto y la velocidad de transmisión según tus necesidades
serial_port = '/dev/ttyS0'  # Puedes necesitar cambiar esto según tu configuración
baud_rate = 9600

ser = serial.Serial(serial_port, baud_rate, timeout=1)

try:
    while True:
       # mensaje = "Hola, mundo\n"
       # ser.write(mensaje.encode('utf-8'))  # Convierte el mensaje a bytes antes de escribirlo en el puerto
       # time.sleep(1)
        data = ser.readline().decode('utf-8').strip()
        
        # Muestra los datos en la pantalla
        #print(f'Datos recibidos: {data}')
        print(data)
except KeyboardInterrupt:
    # Maneja la interrupción del teclado (Ctrl+C) para cerrar el puerto serial antes de salir
    ser.close()
    print("\nPrograma terminado por el usuario.")
