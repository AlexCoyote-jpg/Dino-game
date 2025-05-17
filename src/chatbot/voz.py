import pyttsx3
import logging
import threading

engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('volume', 1.0)

# Selección de voz como ya tienes configurado
for voice in engine.getProperty('voices'):
    name = voice.name.lower()
    if ("eva" in name or "child" in name or "mujer" in name or "female" in name) and "spanish" in name:
        engine.setProperty('voice', voice.id)
        break

# Control de reproducción
hablando = False
thread_actual = None

def _hablar(texto):
    global hablando
    hablando = True
    try:
        engine.say(texto)
        engine.runAndWait()
    except Exception as e:
        logging.error(f"Error en síntesis de voz: {e}")
    hablando = False

def hablar(texto: str):
    global thread_actual
    detener()  # Detener cualquier voz previa antes de iniciar
    thread_actual = threading.Thread(target=_hablar, args=(texto,), daemon=True)
    thread_actual.start()

def detener():
    global hablando
    if hablando:
        engine.stop()
        hablando = False
