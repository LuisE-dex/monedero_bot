from conf import TELEGRAM_TOKEN

import telebot
from telebot.types import BotCommand

from dotenv import load_dotenv

load_dotenv()

class MyBot(telebot.TeleBot):
    def __init__(self, token, **kwargs):
        super().__init__(token, **kwargs)
    
    def send_message(self, chat_id, text, **kwargs):
        bot.send_chat_action(chat_id, "typing")
        return super().send_message(chat_id, text, **kwargs)


bot = MyBot(TELEGRAM_TOKEN)

# Definiendo comandos
bot.set_my_commands([
    BotCommand("start", "Iniciar el bot"),
    BotCommand("balance", "Mostrar saldo actual"),
    BotCommand("ingresar", "Ingresar un monto"),
    BotCommand("extraer", "Extraer un monto"),
    BotCommand("historial", "Ver historial"),
    BotCommand("convertir", "Convertir moneda"),    
    BotCommand("grafica", "Graficar historial"),
    BotCommand("exportar", "Exportar historial"),
])
