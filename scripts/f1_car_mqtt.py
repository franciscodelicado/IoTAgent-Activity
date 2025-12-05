import argparse
import sys
import csv
import time

import paho.mqtt.client as mqtt

def connectMQTT(broker_ip):
    """
    Conecta al broker MQTT y devuelve la instancia del cliente.
    
    :param broker_ip: IP del broker MQTT.

    :return: Instancia del cliente MQTT conectado.
    """
    #TODO: Añadir el código necesario para crear un cliente MQTT conectado al broker en la IP "broker_ip"

def disconnectMQTT(client):
    """
    Desconecta del broker MQTT.
    
    :param client: Instancia del cliente MQTT.
    """
    #TODO: Añadir el código necesario para desconectar el cliente MQTT "client"

def generate_telemetry_data(csv_file):
    """
    Lee datos de telemetría de F1 desde un archivo CSV y genera la carga útil y el tiempo de espera.
    Esta función es un generador.

    :param csv_file: Ruta al archivo CSV con datos de telemetría.

    :return: Yields tuplas de (wait_time, distance, speed, throttle, brake, nGear, rpm).
    """
    try:
        with open(csv_file, 'r', newline='') as file:
            # Omitir la primera línea ("###")
            next(file)

            # Usar la segunda línea como encabezado del CSV
            reader = csv.DictReader(file, delimiter=';')
            print("Encabezado CSV:", reader.fieldnames)
            last_session_time = None

            for row in reader:
                try:
                    session_time = float(row['SessionTime_s'])

                    if last_session_time is None:
                        last_session_time = session_time

                    # Calcular el tiempo de espera antes de enviar el siguiente mensaje
                    wait_time = session_time - last_session_time
                    last_session_time = session_time

                    # Leer valores de telemetría
                    distance=float(row['Distance'])
                    speed=float(row['Speed'])   
                    throttle=float(row['Throttle'])
                    brake=float(row['Brake'])
                    nGear=int(row['nGear'])
                    rpm=float(row['RPM'])

                    yield wait_time, distance, speed, throttle, brake, nGear, rpm

                except (ValueError, KeyError) as e:
                    print(f"Omitiendo fila malformada o con datos faltantes: {row} - Error: {e}")
                    continue

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{csv_file}'.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


def publish_telemetry(client, device_id, api_key, payload):
    """
    Publica con el topic /ul/<api_key>/<device_id>/attrs el contenido de "payload" al broker MQTT.

    :param client: Instancia del cliente MQTT.
    :param device_id: <device_id> del sensor dado de alta en el IoT Agent.
    :param api_key: Clave API del servicio al que pertenece el sensor.
    :param payload: Contenido del mensaje a publicar.
    """
    #TODO: Añadir el código necesario para publicar el "payload" en el tópico adecuado


def respond_cmd(client, userdata, msg):
    """
    Función callback para manejar comandos entrantes.
    Verifica el formato del topic y del payload y envía una respuesta.

    :param client: Instancia del cliente MQTT.
    :param userdata: Datos de usuario asociados al cliente (contiene device_id y api_key).
    :param msg: Mensaje MQTT recibido.
    """

    #TODO: Asegurarnos que el topic contiene el <api_key> y el <device_id> correctos
    #TODO: Verificar que el payload tiene el formato esperado "<device_id>@command|value"
    #TODO: Obtener el commando y el valor asignado a él
    #TODO: Responder al comando con el resultado de la ejecución del comando:
    #               - Si el comando tenía un valor de 1 se ha de responder con el valor "ON"
    #               - Si el comando tenía un valor de 0 se ha de responder con el valor "OFF"
    

def subscribe_to_cmd(client, device_id, api_key):
    """
    Se suscribe al tópico de comandos y configura el callback.

    :param client: Instancia del cliente MQTT.
    :param device_id: <device_id> del sensor dado de alta en el IoT Agent.
    :param api_key: Clave API del servicio al que pertenece el sensor.
    """

    #TODO: Añadir el código necesario para suscribirse al tópico de comandos y configurar el callback como "respond_cmd"



if __name__ == "__main__":
    # Definición de argumentos de entrada del programa
    parser = argparse.ArgumentParser(description="Emulador de un coche de F1 que genera telemetrías")

    parser.add_argument(
        '--file',
        dest='csv_file',
        type=str,
        required=True,
        help='Ruta al archivo CSV con datos de telemetría.'
    )    
    parser.add_argument(
        '--mqtt',
        dest='mqtt_broker',
        type=str,
        required=True,
        help='IP del broker MQTT.'
    )
    parser.add_argument(
        '--device',
        dest='device_id',
        type=str,
        required=True,
        help='<device_id> del dispositivo dado de alta en el IoT Agent.'
    )
    parser.add_argument(
        '--apikey',
        dest='api_key',
        type=str,
        required=True,
        help='<api_key> del servicio al que pertenece el sensor.'
    )

    # Leer los argumentos de entrada
    args = parser.parse_args()


    try:
        # Conecta con el broker MQTT
        clientmqtt=connectMQTT(args.mqtt_broker)

        # Suscribirse al tópico de comandos
        subscribe_to_cmd(clientmqtt, args.device_id, args.api_key)

        # Leer y publicar datos de telemetría
        t0 = time.monotonic()
    
        for wait_time, distance, speed, throttle, brake, nGear, rpm in generate_telemetry_data(args.csv_file):
            if wait_time > 0: # Espero el tiempo necesario antes de enviar el siguiente mensaje
                time.sleep(wait_time)
            
            #TODO: Generar el contenido del mensaje MQTT en formato UltraLigth 2.0 y asignarlo a la variable "payload"

            elapsed_time = time.monotonic() - t0
            print(f"[{elapsed_time:.2f}s] Published: {payload}")

            # Publicar datos de telemetría
            publish_telemetry(clientmqtt, args.device_id, args.api_key, payload)
            
            
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        if 'clientmqtt' in locals():
            disconnectMQTT(clientmqtt)
    