import threading
import queue
import serial
import os
import smbus
import time
import paho.mqtt.publish as publish
import psutil
import string

# Initialize global variables and queues
N_serial = 10
N_read_serial = 10
N_acc = 10
N_temp = 10

avg_x = 0
avg_y = 0
avg_z = 0
avg_temp = 0

avg_x_serial = 0
avg_y_serial = 0
avg_z_serial = 0
avg_temp_serial = 0

queue_N_acc = queue.Queue()
queue_N_temp = queue.Queue()

queue_avg_acc_x = queue.Queue()
queue_avg_acc_y = queue.Queue()
queue_avg_acc_z = queue.Queue()

queue_avg_temp = queue.Queue()

queue_acc_x = queue.Queue()
queue_acc_y = queue.Queue()
queue_acc_z = queue.Queue()

queue_temp = queue.Queue()

# Define the DS18B20 sensor's unique ID
sensor_id = "28-3de104576d55"

# Define the path to the sensor's data
sensor_data_path = f"/sys/bus/w1/devices/{sensor_id}/temperature"

# Initialize the I2C bus
bus = None

# ADXL345 I2C address and bus number
address = 0x53
bus_number = 1

# Register addresses
POWER_CTL = 0x2D
DATA_FORMAT = 0x31
DATAX0 = 0x32
DATAX1 = 0x33
DATAY0 = 0x34
DATAY1 = 0x35
DATAZ0 = 0x36
DATAZ1 = 0x37

# Set the ADXL345 in measurement mode
bus = smbus.SMBus(bus_number)
bus.write_byte_data(address, POWER_CTL, 8)

def read_temperature():
    # Include global variables
    global N_temp
    global queue_avg_temp
    global queue_temp
    global queue_N_temp

    try:
        # Read the raw data from the sensor
        with open(sensor_data_path, "r") as sensor_file:
            lines = sensor_file.read()
            temperature = float(lines) / 1000.0
            queue_temp.put(temperature)

            if not queue_N_temp.empty():
                N_temp = queue_N_temp.get()

            if queue_temp.qsize() >= N_temp:
                avg_temp = 0
                for i in range(N_temp):
                    avg_temp += queue_temp.get()
                avg_temp = avg_temp / N_temp
                queue_avg_temp.put(avg_temp)

    except Exception as e:
        print(f"Error reading temperature: {str(e)}")
        return None

def cloud_communication():
    # Define the variables for MQTT communication
    channel_ID = "2333200"
    mqtt_host = "mqtt3.thingspeak.com"
    mqtt_client_ID = "Gg8PDhUfBC4JKRYfDyQfFgI"
    mqtt_username = "Gg8PDhUfBC4JKRYfDyQfFgI"
    mqtt_password = "hh+9Epa0580Vt1RsMDBQtxc4"
    t_transport = "TCP"
    t_port = 1883

    # Create MQTT topic
    topic = "channels/{}/publish".format(channel_ID)
    global N_serial
    global avg_x_serial
    global avg_y_serial
    global avg_z_serial
    global avg_temp_serial
    payload = "field1={}&field2={:.2f}&field3={:.2f}&field4={:.2f}&field5={:.2f}".format(N_serial, avg_temp_serial, avg_x_serial, avg_y_serial, avg_z_serial)

    try:
        print("Escribiendo Payload =", payload, "a host:", mqtt_host, "clientID =", mqtt_client_ID)
        publish.single(topic, payload, hostname=mqtt_host, transport=t_transport, port=t_port, client_id=mqtt_client_ID, auth={'username': mqtt_username, 'password': mqtt_password})
        time.sleep(20)
    except Exception as e:
        print(e)

# Define the serial port and baud rate
serial_port = '/dev/ttyS0'
baud_rate = 115200

def serial_communication():
    try:
        # Initialize the serial connection
        global avg_x_serial
        global avg_y_serial
        global avg_z_serial
        global avg_temp_serial
        global queue_avg_acc_x
        global queue_avg_acc_y
        global queue_avg_acc_z
        global queue_avg_temp
        global queue_N_temp
        global queue_N_acc
        global N_serial
        global N_read_serial

        if not queue_avg_acc_x.empty():
            avg_x_serial = queue_avg_acc_x.get()

        if not queue_avg_acc_y.empty():
            avg_y_serial = queue_avg_acc_y.get()

        if not queue_avg_acc_z.empty():
            avg_z_serial = queue_avg_acc_z.get()

        if not queue_avg_temp.empty():
            avg_temp_serial = queue_avg_temp.get()

        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        data_to_send = f"{N_serial},{avg_temp_serial},{avg_x_serial},{avg_y_serial},{avg_z_serial}\n"
        ser.write(data_to_send.encode())
        print(data_to_send)

        received_data = ""
        char = ser.readline().decode('ascii')  # Read the full line
        if (char[0:11] == "##PROMEDIO-") and (char[14:17] == "-##"):
            N_read_serial = int(char[11:14])
            if (N_read_serial > 0) and (N_serial != N_read_serial):
                N_serial = N_read_serial
                queue_N_temp.put(N_serial)
                queue_N_acc.put(N_serial)

        # Close the serial connection
        ser.close()

    except serial.SerialException as e:
        print(f"Error: {e}")

def read_accelerometer():
    try:
        global N_acc
        global avg_acc_x
        global avg_acc_y
        global avg_acc_z
        global queue_N_acc
        global queue_acc_x
        global queue_acc_y
        global queue_acc_z
        global queue_avg_acc_x
        global queue_avg_acc_y
        global queue_avg_acc_z

        if bus is not None:
            # Read accelerometer data
            x_low = bus.read_byte_data(address, DATAX0)
            x_high = bus.read_byte_data(address, DATAX1)
            y_low = bus.read_byte_data(address, DATAY0)
            y_high = bus.read_byte_data(address, DATAY1)
            z_low = bus.read_byte_data(address, DATAZ0)
            z_high = bus.read_byte_data(address, DATAZ1)

            # Convert raw data to signed 16-bit values
            x_acceleration = (x_high << 8 | x_low) if x_high < 128 else -((255 - x_high) << 8 | (255 - x_low))
            y_acceleration = (y_high << 8 | y_low) if y_high < 128 else -((255 - y_high) << 8 | (255 - y_low))
            z_acceleration = (z_high << 8 | z_low) if z_high < 128 else -((255 - z_high) << 8 | (255 - z_low))

            # Print the acceleration data
            queue_acc_x.put(x_acceleration)
            queue_acc_y.put(y_acceleration)
            queue_acc_z.put(z_acceleration)

            if not queue_N_acc.empty():
                N_acc = queue_N_acc.get()

            if queue_acc_x.qsize() >= N_acc:
                avg_acc_x = 0
                for i in range(N_acc):
                    avg_acc_x += queue_acc_x.get()
                avg_acc_x = avg_acc_x / N_acc
                queue_avg_acc_x.put(avg_acc_x)

            if queue_acc_y.qsize() >= N_acc:
                avg_acc_y = 0
                for i in range(N_acc):
                    avg_acc_y += queue_acc_y.get()
                avg_acc_y = avg_acc_y / N_acc
                queue_avg_acc_y.put(avg_acc_y)

            if queue_acc_z.qsize() >= N_acc:
                avg_acc_z = 0
                for i in range(N_acc):
                    avg_acc_z += queue_acc_z.get()
                avg_acc_z = avg_acc_z / N_acc
                queue_avg_acc_z.put(avg_acc_z)
    except Exception as e:
        print(f"Error reading accelerometer: {str(e)}")

# Create threads for each function
tt_serial = threading.Thread(target=serial_communication)
tt_cloud = threading.Thread(target=cloud_communication)

while True:
    # Start new threads for accelerometer and temperature
    tt_acc = threading.Thread(target=read_accelerometer)
    tt_temp = threading.Thread(target=read_temperature)

    # Start the threads
    tt_acc.start()
    tt_temp.start()

    # Wait for the accelerometer and temperature threads to finish
    tt_acc.join()
    tt_temp.join()

    # Check if the serial_communication thread is still running
    if not tt_serial.is_alive():
        # If it's not running, restart it
        tt_serial = threading.Thread(target=serial_communication)
        tt_serial.start()
    # Do the same with the cloud thread
    if not tt_cloud.is_alive():
        tt_cloud = threading.Thread(target=cloud_communication)
        tt_cloud.start()
