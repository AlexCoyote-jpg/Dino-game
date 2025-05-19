from gtts import gTTS
import os
import threading
from queue import Queue, Empty
import uuid
import pygame
import time

# Inicializar pygame para reproducción de audio
pygame.mixer.init()

# Control de reproducción
hablando = threading.Event()
cola_texto = Queue()

def _eliminar_archivo(filename):
    """Intentar eliminar el archivo después de un breve retraso."""
    for _ in range(5):  # Intentar hasta 5 veces
        try:
            if os.path.exists(filename):
                os.remove(filename)
                break
        except PermissionError:
            time.sleep(0.1)  # Esperar antes de intentar nuevamente

def _procesar_cola():
    while True:
        try:
            texto = cola_texto.get(timeout=0.1)  # Esperar un tiempo limitado para evitar bloqueos
            if texto is None:  # Señal para detener el hilo
                break
            try:
                # Generar un nombre de archivo único
                filename = f"output_{uuid.uuid4().hex}.mp3"
                tts = gTTS(text=texto, lang='es')
                tts.save(filename)
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
            except Exception as e:
                print(f"Error en síntesis de voz: {e}")
            finally:
                # Asegurarse de que el archivo no esté en uso antes de eliminarlo
                pygame.mixer.music.unload()
                threading.Thread(target=_eliminar_archivo, args=(filename,), daemon=True).start()
                hablando.clear()
        except Empty:
            continue

hilo_voz = threading.Thread(target=_procesar_cola, daemon=True)
hilo_voz.start()

def hablar(texto: str):
    detener()  # Detener cualquier voz previa antes de iniciar
    hablando.set()
    cola_texto.put(texto)

def detener():
    if hablando.is_set():
        pygame.mixer.music.stop()
        hablando.clear()

def cerrar_hilo():
    cola_texto.put(None)
    hilo_voz.join()
