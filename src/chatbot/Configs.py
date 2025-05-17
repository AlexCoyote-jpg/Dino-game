import json
import os

def cargar_json(ruta):
    """
    Carga y devuelve el contenido de un archivo JSON.
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

class ServicioConexion:
    def __init__(self, nombre, datos):
        self.nombre = nombre
        self.api_key = datos.get("api_key")
        self.model = datos.get("model")


def cargar_servicios_conexion(ruta):
    """
    Devuelve un diccionario de instancias ServicioConexion por cada servicio.
    """
    datos = cargar_json(ruta)
    return {nombre: ServicioConexion(nombre, cfg) for nombre, cfg in datos.get("servicios", {}).items()}

def cargar_conexiones(ruta):
    """
    Devuelve el diccionario de configuraciones de conexión.
    """
    datos = cargar_json(ruta)
    return datos.get("conexion", {})

def cargar_prompt_inicial(ruta):
    """
    Devuelve el prompt inicial definido en la configuración.
    """
    datos = cargar_json(ruta)
    return datos.get("prompt_inicial", "")


# Instancias globales Conexion (ajusta las rutas si es necesario)
ruta_conex = os.path.join(os.path.dirname(__file__), "../Settings/Conexion_Settings.json")
servicios = cargar_servicios_conexion(ruta_conex)
conexiones = cargar_conexiones(ruta_conex)
PROMP_INICIAL = cargar_prompt_inicial(ruta_conex)

# Instancia de la clase ServicioConexion para el servicio de AI
DEEPSEEK = servicios.get("deepseek")
LLAMA = servicios.get("llama")
# Instancia de la clase ServicioConexion para el servicio de NVIDIA
nvidia_servicio = servicios.get("nvidia")


