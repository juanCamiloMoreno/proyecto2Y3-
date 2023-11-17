import smbus
import time

# Dirección del MPU-6050 (puedes verificarla usando el comando "i2cdetect -y 1" en la terminal)
MPU6050_ADDR = 0x68

# Registros para configurar el MPU-6050
PWR_MGMT_1 = 0x6B
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C

# Inicializa el bus I2C
bus = smbus.SMBus(1)

# Configura el MPU-6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
bus.write_byte_data(MPU6050_ADDR, CONFIG, 0)
bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, 0)
bus.write_byte_data(MPU6050_ADDR, ACCEL_CONFIG, 0)

# Función para leer los valores del acelerómetro
def read_accel_data(addr):
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = ((high << 8) | low)
    if value > 32767:
        value -= 65536
    return value

try:
    while True:
        # Lee los valores del acelerómetro
        accel_x = read_accel_data(0x3B)
        accel_y = read_accel_data(0x3D)
        accel_z = read_accel_data(0x3F)

        # Muestra los valores en pantalla
        print(f"Aceleración en el eje X: {accel_x}")
        print(f"Aceleración en el eje Y: {accel_y}")
        print(f"Aceleración en el eje Z: {accel_z}")

        # Espera 1 segundo antes de la siguiente lectura
        time.sleep(1)

except KeyboardInterrupt:
    print("Lectura de acelerómetro detenida.")

