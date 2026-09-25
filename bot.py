import os
import time
import requests
import telebot
from flask import Flask
from threading import Thread
from datetime import date, timedelta

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

ABB_BASE_URL = os.environ.get("ABB_BASE_URL")
ABB_TOKEN = os.environ.get("ABB_TOKEN")
ABB_ACCOUNT = os.environ.get("ABB_ACCOUNT")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

last_transaction = None


@app.route("/")
def home():
    return "Bot işləyir!"


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🤖 Bot aktivdir!\nABB əməliyyatları izlənilir."
    )


def check_abb():
    global last_transaction

    today = date.today()
    yesterday = today - timedelta(days=1)

    url = f"{ABB_BASE_URL}/payments/account/statement"

    headers = {
        "Authorization": f"Bearer {ABB_TOKEN}"
    }

    params = {
        "from-date": str(yesterday),
        "to-date": str(today),
        "page-size": 50,
        "page": 0,
        "operation-type": "A",
        "account": ABB_ACCOUNT
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=20
        )

        print("ABB status:", response.status_code)

        if response.status_code != 200:
            print("ABB cavabı:", response.text[:500])
            return

        data = response.json()

        transactions = (
            data.get("transaction", {})
            .get("transactions", [])
        )

        if not transactions:
            print("Əməliyyat tapılmadı.")
            return

        transactions.reverse()

        for tr in transactions:

            transaction_id = (
                tr.get("rrn")
                or tr.get("trnRef")
                or tr.get("messageId")
            )

            if not transaction_id:
                continue

            if last_transaction is None:
                last_transaction = transaction_id
                continue

            if transaction_id == last_transaction:
                continue

            last_transaction = transaction_id

            amount = tr.get("crAmount", 0)

            if amount and float(amount) > 0:

                text = (
                    "💰 YENİ MƏDAXİL\n\n"
                    f"💵 Məbləğ: {amount} AZN\n"
                    f"👤 Göndərən: {tr.get('fullName', '-')}\n"
                    f"📅 Tarix: {tr.get('trnDate', '-')}\n"
                    f"📝 Açıqlama: {tr.get('trnDesc', '-')}\n"
                    f"🔢 RRN: {tr.get('rrn', '-')}"
                )

                bot.send_message(CHAT_ID, text)

    except Exception as e:
        print("ABB bağlantı xətası:", e)


def monitor():
    while True:
        check_abb()
        time.sleep(30)


Thread(target=monitor, daemon=True).start()


if __name__ == "__main__":
    Thread(
        target=bot.infinity_polling,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=8080
    )
