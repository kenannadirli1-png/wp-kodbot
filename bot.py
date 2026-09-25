import os
from threading import Thread
from flask import Flask
import telebot

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot işləyir ✅"

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Salam! Bot işləyir ✅")

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
