import argparse
import json
from flask import Flask, request, jsonify
import requests
import threading

# Create a Flask application instance
app = Flask(__name__)

drs=False   # Estado actual del DRS
orion=None  # IP:puerto del Orion Context Broker

def setDRSCommand(id, state):
    """
    Envía el cambio de estado DRS al Orion Context Broker.

    :param id: ID del vehículo, debe ser un <entity_id> dado de alta en el IoT Agent.
    :param state: Nuevo estado DRS (True para activar, False para desactivar).
    """    
    #TODO: enviar un REQUEST PATCH al Orion Context Broker para actualizar el atributo "drs" del vehículo con ID "id" y valor "state"
    #      OJO: Hay que incluir las cabeceras "fiware-service" y "fiware-servicepath" en la petición HTTP
    #
    # Sugerencia: Utilizar la librería "requests" de Python para enviar la petición HTTP PATCH
    #



def controlDrs(id, speed, brake):
    """
    Controla el estado del DRS basado en la velocidad y el frenado.
    El DRS se activa si está desactivado y la velocidad es >= 200 km/h y el frenado < 1 (sin frenar).
    Se desactiva si está activado la velocidad es < 200 km/h o el frenado >= 1 (frenando).

    :param id: ID del vehículo, debe ser un <entity_id> dado de alta en el IoT Agent.
    :param speed: Velocidad actual del vehículo.
    :param brake: Nivel de frenado actual del vehículo.
    """
    
    global drs # Usar la variable global drs

    #TODO: Implementar la lógica de control del DRS
    #      - Si el DRS está desactivado y la velocidad es >= 200 km/h y el frenado < 1, activar el DRS
    #      - Si el DRS está activado y la velocidad es < 200 km/h o el frenado >= 1, desactivar el DRS
    # 
    #     - Llamar a la función setDRSCommand(id, state) para enviar el cambio de estado al Orion Context Broker.
    #
    # Sugerencia: Para no tener que esperar la respuesta HTTP del Orion Context Broker, se aconseja utilizar un hilo (threading.Thread) para llamar a la función setDRSCommand(id, state)

def main():
    
    # Definición de argumentos de entrada del programa
    parser = argparse.ArgumentParser(description="Servico Web que solo atiende peticiones POST.")
    # Puerto en el que escucha el servicio web
    parser.add_argument(
        '--port',
        dest='port',
        type=int,
        required=True,
        help='Puerto en el que escucha el servicio web.'
    )
    parser.add_argument(
        '--endpoint',
        dest='endpoint',
        type=str,
        required=True,
        help='Ruta del "endpoint" para peticiones POST (ejemplo: /data).'
    )
    global orion
    parser.add_argument(
        '--orion',
        dest='orion',
        type=str,
        required=False,
        help='IP:puerto de Orion. Valor por defecto "localhost:1026".',
        default='localhost:1026'
    )

    # Leer los argumentos de entrada
    args = parser.parse_args()
    orion=args.orion

    # Crear dinámicamente la ruta basada en el argumento de línea de comandos
    @app.route(args.endpoint, methods=['POST'])
    def handle_post_request():
        """
        Atiende las peticiones POST entrantes en el endpoint especificado.
        Analiza la carga útil JSON y devuelve una respuesta 200 OK.
        """
        if not request.is_json:
            return jsonify({"ERROR": "El contenido debe ser JSON"}), 400

        try:
            # Obtener y analizar la carga útil JSON de la solicitud
            data = request.get_json()
            
            #print(f"Payload JSON recibido y analizado: {json.dumps(data, indent=2)}")
                     
#TODO: Extraer los valores de "car_id"=<device_id>, "speed" y "brake" del JSON recibido            

            print(f'Car: {car_id}, Speed: {speed} km/h, Brake: {brake}') # Debug info
            
            controlDrs(car_id, speed, brake)
        
            # Respuesta HTTP 200 OK
            return jsonify({"status": "success", "message": "Data received"}), 200
        except Exception as e:
            # Manejar posibles errores durante el análisis o procesamiento del JSON
            print(f"Ocurrió un error: {e}")
            return jsonify({"error": "JSON inválido o error del servidor"}), 500

    # Ejecutar la aplicación Flask en el puerto especificado, accesible desde cualquier interfaz de red
    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    # Para ejecutar el script directamente:
    #
    #  python drs_controller.py --port 5000 --endpoint /data [--orion localhost:1026]
    main()