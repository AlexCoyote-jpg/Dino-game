import time
from voz_nube import hablar, detener, cerrar_hilo

# Prueba de hablar
print("Iniciando prueba de hablar...")
hablar("Hola, esta es una prueba de síntesis de voz.")
time.sleep(2)  # Esperar para permitir que hable

# Prueba de detener
print("Deteniendo la voz...")
detener()
time.sleep(1)  # Esperar para asegurarse de que se detuvo

# Prueba de hablar nuevamente
print("Iniciando otra prueba de hablar...")
hablar("Esta es otra prueba después de detener la voz.")
time.sleep(3)  # Esperar para permitir que hable

# Cerrar hilo de voz
cerrar_hilo()
print("Pruebas completadas.")
