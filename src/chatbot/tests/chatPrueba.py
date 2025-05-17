from chatbot.chat import ChatBot

def callback():
    print("Callback ejecutado.")

def main():
    bot = ChatBot()
    print("Enviando mensaje al bot...")
    exito = bot.procesar_input("Hola, ¿cómo estás?", callback)
    if exito:
        print("Mensaje procesado correctamente.")
    else:
        print("No se pudo procesar el mensaje.")

    print("\nHistorial de la conversación:")
    for rol, mensaje in bot.obtener_historial():
        print(f"{rol}: {mensaje}")

if __name__ == "__main__":
    main()