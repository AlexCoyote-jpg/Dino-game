# resources.py
"""
Gestión centralizada de recursos (imágenes, sonidos, fuentes, etc.).
"""

def load_images(path):
    # Implementa la carga funcional de imágenes desde un directorio
    import os
    import pygame
    images = {}
    for file in os.listdir(path):
        if file.endswith('.png'):
            name = os.path.splitext(file)[0]
            images[name] = pygame.image.load(os.path.join(path, file)).convert_alpha()
    return images

def load_sounds(path):
    # Implementa la carga funcional de sonidos desde un directorio
    import os
    import pygame
    sounds = {}
    for file in os.listdir(path):
        if file.endswith('.wav'):
            name = os.path.splitext(file)[0]
            sounds[name] = pygame.mixer.Sound(os.path.join(path, file))
    return sounds

# El acceso a recursos se hace pasando los diccionarios resultantes
# Ejemplo: images = load_images('assets/imagenes')
#          img = images['dino1']
