from openai import OpenAI
import logging
import threading
from .Configs import conexiones, PROMP_INICIAL

logging.basicConfig(level=logging.INFO)


def obtener_respuesta(user_input: str, modelo: str, servicio_key: str) -> str:
    """
    Envía el mensaje del usuario a la API y retorna la respuesta generada.
    """
    # Validar que el input no esté vacío
    user_input = user_input.strip()
    if not user_input:
        logging.error("Error: Se intentó enviar un mensaje vacío a la API")
        return "No puedo procesar mensajes vacíos. Por favor, escribe algo."
    
    prompt = PROMP_INICIAL
    conexion = conexiones["nvidia"]
    logging.info(f"Enviando solicitud a la API con modelo: {modelo}")
    try:
        # Configuración de la API
        client = OpenAI(
            base_url=conexion["url"],
            api_key=servicio_key,
         )
        completion = client.chat.completions.create(
           
            model=modelo,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=conexion.get("temperature"),
            top_p=conexion.get("top_p"),
            max_tokens=conexion.get("max_tokens"),
            stream=conexion.get("stream")
        )
        response_chunks = []
        for chunk in completion:
            delta_content = getattr(chunk.choices[0].delta, "content", None)
            if delta_content:
                response_chunks.append(delta_content)
        logging.info("Solicitud enviada correctamente a la API.")
        return "".join(response_chunks)
    except Exception as e:
        logging.error(f"Error al procesar la respuesta de la API: {e}")
        return "Ocurrió un error al procesar la respuesta de la API."


def obtener_respuesta_async(user_input: str, modelo: str, servicio_key: str, callback):
    """
    Ejecuta obtener_respuesta en un hilo aparte y llama a callback con la respuesta.
    """
    def run():
        respuesta = obtener_respuesta(user_input, modelo, servicio_key)
        callback(respuesta)
    hilo = threading.Thread(target=run)
    hilo.start()


