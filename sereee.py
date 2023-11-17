import serial

# Configura el puerto serial
ser = serial.Serial('/dev/ttyS0', 9600)  # Ajusta la velocidad de baudios según tu configuración

try:
    while True:
        # Lee datos desde el puerto serial
        data = ser.readline().decode('utf-8').strip()
        
        # Muestra los datos en la pantalla
        print(f'Datos recibidos: {data}')

except KeyboardInterrupt:
    # Maneja la interrupción del teclado (Ctrl+C)
    print("Programa interrumpido por el usuario.")

finally:
    # Cierra el puerto serial al finalizar
    ser.close()
