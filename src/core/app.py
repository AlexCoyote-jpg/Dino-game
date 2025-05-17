# app.py
import logging
import os
import pygame
from core.config import load_config
from core.resources import load_images, load_sounds
from core.decoration.background import FondoAnimado
from ui.menu_principal import run_menu_principal

def run_app(debug=False):
    logging.basicConfig(level=logging.INFO)
    pygame.init()
    if debug:
        print("Modo debug activado")
    ruta_config = os.path.join(os.path.dirname(__file__), "../Settings/Configuracion.json")
    config = load_config(ruta_config)
    ancho = config["pantalla"] .get("ancho")
    alto = config["pantalla"] .get("alto")
    pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
    pygame.display.set_caption("Jugando con Dino")
    images = load_images("assets/imagenes")
    sounds = load_sounds("assets/sonidos")
    fondo = FondoAnimado(ancho, alto)
    run_menu_principal(pantalla, fondo, images, sounds, config)


