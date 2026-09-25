import os
import random
import string
from threading import Thread
from flask import Flask
import telebot

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot işləyir ✅"

def generate_code(amount):
    chars = string.ascii_uppercase + string.digits
    code = "".join(random.choices(chars, k=8))
    return f"{amount} AZN-KOD-{code}"

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Salam! Bot işləyir ✅\n\n3 AZN kodu üçün: ..ver 3")

@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith("..ver"))
def give_code(message):
    parts = message.text.split()

    if len(parts) != 2:
        bot.reply_to(message, "İstifadə: ..ver 3")
        return

    try:
        amount = int(parts[1])
    except ValueError:
        bot.reply_to(message, "Məbləğ rəqəm olmalıdır. Məsələn: ..ver 3")
        return

    if amount not in [3, 5, 10]:
        bot.reply_to(message, "Hazırda yalnız 3, 5 və 10 AZN mümkündür.")
        return

    code = generate_code(amount)
    bot.reply_to(message, f"🎁 {amount} AZN-lik kodun:\n\n`{code}`", parse_mode="Markdown")

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
