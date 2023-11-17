import serial

def main(puerto_serial):
    with serial.Serial("/dev/ttyS0", 115200, timeout=1) as ser:
        try:
            while True:
                mensaje = ser.readline().decode().strip()
                print(mensaje)
        except KeyboardInterrupt:
            # Manejar la interrupción del teclado (Ctrl+C) para cerrar el puerto serial antes de salir
            ser.close()
            print("\nPrograma terminado por el usuario.")

if __name__ == "__main__":
    puerto_serial = "/dev/ttyS0"  # Ajusta esto según tu configuración
    main(puerto_serial)
