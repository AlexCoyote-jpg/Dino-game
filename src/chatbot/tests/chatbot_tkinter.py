import tkinter as tk
from tkinter import scrolledtext
import threading
from chatbot.Configs import LLAMA
from chatbot.Conexion import obtener_respuesta

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        # Área de conversación
        self.conversation_frame = tk.Frame(root)
        self.conversation_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.conversation = scrolledtext.ScrolledText(self.conversation_frame, wrap=tk.WORD, state="disabled")
        self.conversation.pack(fill=tk.BOTH, expand=True)
        
        # Área de entrada
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.input_field = tk.Entry(self.input_frame)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(self.input_frame, text="Enviar", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Mensaje inicial
        self.display_message("Chatbot", "¡Hola! ¿En qué puedo ayudarte?")
        
        # Dar foco al campo de entrada
        self.input_field.focus_set()
    
    def display_message(self, sender, message):
        self.conversation.config(state="normal")
        self.conversation.insert(tk.END, f"{sender}: {message}\n\n")
        self.conversation.see(tk.END)
        self.conversation.config(state="disabled")
    
    def send_message(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        
        self.input_field.delete(0, tk.END)
        self.display_message("Tú", user_input)
        
        # Deshabilitar entrada mientras procesa
        self.input_field.config(state="disabled")
        self.send_button.config(state="disabled")
        
        # Procesar respuesta en segundo plano
        threading.Thread(target=self.get_bot_response, args=(user_input,), daemon=True).start()
    
    def get_bot_response(self, user_input):
        response = obtener_respuesta(user_input, LLAMA.model, LLAMA.api_key)
        
        # Actualizar UI en el hilo principal
        self.root.after(0, lambda: self.display_bot_response(response))
    
    def display_bot_response(self, response):
        self.display_message("Chatbot", response)
        
        # Rehabilitar entrada
        self.input_field.config(state="normal")
        self.send_button.config(state="normal")
        self.input_field.focus_set()

def run_chatbot():
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_chatbot()