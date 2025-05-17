# Juego_Dino
Juego Educativo con tematica de Dinosaurios enfocado en niños entre 6 y 10 años.Proyectos con componentes de IA


Como Ejecutarlo
Creas un entorno Virtual: python3 -m venv .venv (cambia el nombre si quieres )
Activar el entorno
-Linux (codespace tambien aplica):
source .venv/bin/activate
-Windows: 
.venv\Scripts\Activate    
En caso de de que no te deje por la seguridad de windows pon el comando:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

Instala las libreria al entorno virtual: pip install -r requirements.txt

Listo ahora solo ejecuta main.py 


Si el entorno virtual no cuenta con alguna libreria o no cargo todas:
(Recuerda debe estar activado el entorno virtual)
Tiene que tener instalado python python --version
Liberias
-PIP: python get-pip.py,pip install --upgrade pip, pip --versión,
-PYGAME Y OPEINAI: pip install pygame openai
-Pygame-gui:pip install pygame_gui
-Emojis: pip install emoji

Nota: Si quieres instalar automaticamente todas las libreria ejecuta python setup.py 

Para guardar las dependencias : 
-Ejecuta : pip freeze > requirements.txt
-Modifica: setup.py

--Menu Principal--
-home
![home](image.png)
-selector game by nivel
![nivel](image-1.png)
--game example--
![alt text](image-2.png)