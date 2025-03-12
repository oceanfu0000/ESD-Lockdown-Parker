from flask import Flask
from telegram_api import telegram_blueprint

app = Flask(__name__)

# Register the Telegram Blueprint
app.register_blueprint(telegram_blueprint, url_prefix="/telegram")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
