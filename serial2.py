import serial

def leer_trama(ser):
    trama = ser.readline().decode().strip()
    if trama.startswith("##PROMEDIO-") and trama.endswith("-##"):
        try:
            ventana_size = int(trama.split('-')[2])
            return ventana_size
        except (ValueError, IndexError):
            pass
    return None

def main(puerto_serial):
    with serial.Serial(puerto_serial, 115200, timeout=1) as ser:
        while True:
            ventana_size = leer_trama(ser)

            if ventana_size is not None:
                print(f"Tamaño de la ventana: {ventana_size}")

if __name__ == "__main__":
    puerto_serial = "/dev/ttyS0"  # Ajusta esto según tu configuración
    main(puerto_serial)
