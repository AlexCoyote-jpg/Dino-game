from chatbot.chat import ChatBot

def test_chatbot():
    bot = ChatBot()

    print('--- Prueba: mensaje normal ---')
    def callback1(respuesta):
        print('Respuesta:', respuesta)
        print('Historial:', bot.obtener_historial())
    bot.procesar_input('¿Cómo hago una suma?', callback1)

    print('\n--- Prueba: mensaje vacío ---')
    def callback2(respuesta):
        print('Respuesta:', respuesta)
        print('Historial:', bot.obtener_historial())
    bot.procesar_input('   ', callback2)

if __name__ == '__main__':
    test_chatbot()