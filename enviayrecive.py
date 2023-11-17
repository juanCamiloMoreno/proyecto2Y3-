import serial
import queue
import threading
import time

# Cola global para almacenar valores de lectura
cola_lecturas = queue.Queue()

# Variable global para el número de lecturas promedio
N_lecturas = 10

# Variable global para indicar si los hilos deben continuar ejecutándose
ejecucion_activa = True

# Función para cambiar el valor de N_lecturas
def cambiar_numero_lecturas(nuevo_valor):
    global N_lecturas
    N_lecturas = nuevo_valor

# Función que escribe el promedio de las últimas N lecturas en un puerto serial
def escribir_promedio_puerto_serial():
    while ejecucion_activa:
        try:
            # Obtener los últimos N valores de la cola
            datos = [cola_lecturas.get_nowait() for _ in range(min(cola_lecturas.qsize(), N_lecturas))]

            if datos:
                # Calcular el promedio de las últimas N lecturas
                promedio = sum(datos) / len(datos)

                # Formatear la trama a enviar
                trama = "##PROMEDIO-{}-##\n".format(int(promedio))

                # Configurar el puerto serial (ajusta el nombre del puerto según tu configuración)
                puerto_serial = serial.Serial('/dev/ttyS0', 115200, timeout=1)

                # Escribir la trama en el puerto serial
                puerto_serial.write(trama.encode())

                # Cerrar el puerto serial
                puerto_serial.close()

        except queue.Empty:
            # La cola está vacía, no hay datos para procesar
            pass

        time.sleep(1)  # Espera para no sobrecargar el hilo

# Función para leer desde el puerto serial y agregar el valor a la cola
# ...

# Función para leer desde el puerto serial y agregar el valor a la cola
def leer_puerto_serial():
    # Configurar el puerto serial (ajusta el nombre del puerto según tu configuración)
    puerto_serial = serial.Serial('/dev/ttyS0', 115200, timeout=1)

    while ejecucion_activa:
        # Leer desde el puerto serial
        bytes_leidos = puerto_serial.readline()
        
        try:
            mensaje = bytes_leidos.decode('utf-8').strip()
        except UnicodeDecodeError:
            # Intentar con otra codificación si hay un error
            mensaje = bytes_leidos.decode('latin-1').strip()

        # Verificar si el mensaje sigue el formato esperado
        if mensaje.startswith("##PROMEDIO-") and mensaje.endswith("-##"):
            # Extraer el valor de NNN de la trama
            partes_mensaje = mensaje.split("-")
            if len(partes_mensaje) == 5:  # Verificar que hay suficientes partes en el mensaje
                valor_nnn = partes_mensaje[2]
                
                try:
                    valor_nnn = int(valor_nnn)
                    # Cambiar el número de lecturas para el promedio
                    cambiar_numero_lecturas(valor_nnn)
                except ValueError:
                    print("Error: No se pudo convertir a entero:", valor_nnn)
            else:
                print("Error: El mensaje no tiene el formato esperado:", mensaje)

        # Si el mensaje no sigue el formato esperado, intentar convertir a entero
        else:
            try:
                valor_lectura = int(mensaje)
                cola_lecturas.put(valor_lectura)
            except ValueError:
                # El mensaje no es un número válido, ignorarlo
                print("Error: No se pudo convertir a entero:", mensaje)

    # Cerrar el puerto serial
    puerto_serial.close()

# ...

# Crear hilos
hilo_escritura = threading.Thread(target=escribir_promedio_puerto_serial)
hilo_lectura = threading.Thread(target=leer_puerto_serial)

# Iniciar hilos
hilo_escritura.start()
hilo_lectura.start()

# Esperar a que ambos hilos terminen
hilo_escritura.join()
hilo_lectura.join()
