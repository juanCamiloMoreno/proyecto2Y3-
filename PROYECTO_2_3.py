import smbus
import math
import time
# Dirección del MPU-6050
MPU6050_ADDR = 0x68

# Registros del MPU-6050
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# Inicializa el bus I2C
bus = smbus.SMBus(1)

# Configura el MPU-6050 para activarlo
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

# Función para leer valores
def read_word(reg):
    high = bus.read_byte_data(MPU6050_ADDR, reg)
    low = bus.read_byte_data(MPU6050_ADDR, reg + 1)
    value = (high << 8) | low
    if value >= 0x8000:
        return -((65535 - value) + 1)
    else:
        return value

def read_accel():
    accel_x = read_word(ACCEL_XOUT_H)
    accel_y = read_word(ACCEL_YOUT_H)
    accel_z = read_word(ACCEL_ZOUT_H)
    return (accel_x, accel_y, accel_z)

def read_gyro():
    gyro_x = read_word(GYRO_XOUT_H)
    gyro_y = read_word(GYRO_YOUT_H)
    gyro_z = read_word(GYRO_ZOUT_H)
    return (gyro_x, gyro_y, gyro_z)

try:
    while True:
        accel_data = read_accel()
        gyro_data = read_gyro()
        
        # Escalado de los valores
        accel_scale = 16384.0  # 2g en el rango de ±2g
        gyro_scale = 131.0    # 250 grados por segundo en el rango de ±250 grados/segundo

        accel_x, accel_y, accel_z = [round(x / accel_scale, 2) for x in accel_data]
        gyro_x, gyro_y, gyro_z = [round(x / gyro_scale, 2) for x in gyro_data]

        print(f"Aceleración (g): X={accel_x}, Y={accel_y}, Z={accel_z}")
        print(f"Velocidad angular (°/s): X={gyro_x}, Y={gyro_y}, Z={gyro_z}")

        time.sleep(1)  # Espera 1 segundo antes de la siguiente lectura

except KeyboardInterrupt:
    print("Lectura del MPU-6050 detenida.")
