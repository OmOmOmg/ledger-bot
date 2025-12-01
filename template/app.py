from flask import Flask
from flask import request
from flask import abort

import requests
import json
import telebot

bot = telebot.TeleBot("YOUR_TELEGRAM_API_HERE", threaded=False)

app = Flask('__name__')


# flask app route for web-hook
@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':

        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])

        else:
            abort(403)

    return 'OK'


# handle start command
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Введите запрос в формате 12.34 USD RUB\n")


# receive imput from user
@bot.message_handler(content_types=["text"])
def handle_text(message):
    try:
        sum_x, base, y = message.text.split()
        base = base.upper()
        y = y.upper()

        api_key = 'YOUR_API_KEY_HERE'
        api_endpoint = f'https://openexchangerates.org/api/latest.json?app_id={api_key}'
        response = requests.get(api_endpoint)
        j = json.loads(response.text)

        if base == 'USD':
            cur1 = 1
        else:
            cur1 = 1 / j['rates'][base]

        cur2 = j['rates'][y]

        sum_y_1 = cur1 * cur2
        sum_y = float(sum_x) * sum_y_1

        bot.reply_to(message, f'1 {base} = {sum_y_1:.2f} {y}')
        if float(sum_x) > 1:
            bot.reply_to(message, f'{sum_x} {base} = {sum_y:.2f} {y}')


    except:
        bot.reply_to(message, "Что-то пошло не так. Проверьте формат вводимых данных.")


if __name__ == "__main__":
    app.run(debug=True)