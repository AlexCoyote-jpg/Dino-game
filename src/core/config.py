# config.py
import os
"""
Gestión de configuración global y constantes del juego.
"""
import json

def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"No se encontró el archivo: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
    
class Configuracion:
    def __init__(self, datos):
        self.pantalla = datos.get("pantalla", {})
        return datos

def cargar_configuracion(ruta):
    """
    Carga y devuelve la configuración general.
    """
    datos = load_config(ruta)
    return Configuracion(datos)

# Ejemplo de uso:
# config = load_config('Settings/Configuracion.json')
# ancho = config.get('ancho', 900)
