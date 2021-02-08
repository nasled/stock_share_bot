
import time
import json
import requests
from datetime import datetime
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TELEGRAM_BOT_TOKEN = "---"

class TelegramBot:
    def __init__(self):
        self.help_message = "Available commands: /hello, /predict STOCK_ID START_YEAR \r\n\r\nExample: /predict SENS 2012"
        self.min_from_year = 2012
        self.temp_file_name = 'regression_chart.png'

    def hello(self, update: Update, context: CallbackContext) -> None:
        user = update.message.from_user
        update.message.reply_text('Hello, {}! {}'.format(user.first_name, self.help_message))

    def echo(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Sorry, the command is unknown: ' + update.message.text + '. \r\n\r\n' + self.help_message)

    def predict(self, update: Update, context: CallbackContext) -> None:
        error_message = False
        update.message.reply_text('Generating...')
        # try:
        if len(context.args[0]) == 0:
            update.message.reply_text('Please provide stock ID')
            return

        stock_id = context.args[0]
        from_date = str(self.min_from_year)
        if len(context.args) > 1:
            from_date = context.args[1]
            if len(from_date) == 4:
                from_date = from_date + "-01-01"
        else:
            from_date = '2012-01-01'


        print('parsing...', stock_id, from_date)
        bot = NasdaqExchangeParser(stock_id, from_date)
        result = bot.run(bot.chart_command)
        if result == True:
            context.bot.send_photo(update.message.chat['id'], photo=open(self.temp_file_name, 'rb'))
        else:
            update.message.reply_text(result)


class NasdaqExchangeParser:
    def __init__(self, stock_id, from_date = '2012-01-01', to_date = '', output_file = ''):
        self.endpoint = "https://api.nasdaq.com/api/quote/"
        self.stock_id = stock_id
        self.chart_command = "chart"
        self.info_command = "info"
        self.client_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
            "Accept": "application/json, text/plain, */*",
            "TE": "Trailers"
        }
        self.from_date = from_date
        self.to_date = to_date
        self.output_file = "regression_chart.png"

    def get_url(self, stock_id, command):
        return self.endpoint + stock_id + "/" + command

    def run(self, command):
        if command == self.info_command:
            payload = {"assetclass": "stocks"}
            info_response = requests.get(self.get_url(self.stock_id, self.info_command), headers=self.headers, params=payload)
            # print(info_response.url)
            # print(info_response.text)

        else:
            if self.to_date == '':
                self.to_date = datetime.today().strftime('%Y-%m-%d')

            payload = {
                "assetclass": "stocks",
                "fromdate": self.from_date,
                "todate": self.to_date,
            }

            chart_response = requests.get(self.get_url(self.stock_id, self.chart_command), headers=self.client_headers, params=payload)
            print("endpoint URL:", chart_response.url)
            # print("endpoint length response:", + len(chart_response.text))

            json_object = json.loads(chart_response.text)
            # print(json_object)
            print("endpoint response code:", json_object['status']['rCode'])

            if json_object['status']['rCode'] == 200:
                chart_object = json_object['data']['chart']
                print("total chart objects found:", len(chart_object))

                dates_raw = []
                values_raw = []
                for c in chart_object:
                    seconds = c['x']/1000
                    date = datetime.fromtimestamp(seconds).strftime('%Y-%m-%d')
                    value = c['y']
                    dates_raw.append(seconds)
                    values_raw.append(value)

                x = np.array(list(range(0, len(dates_raw))))
                y = np.array(values_raw)
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                curve = intercept + slope * x
                plt.figure(figsize=(18, 6))
                plt.plot(x, y, label='value')
                plt.plot(x, curve, 'r', label='forecast')
                plt.legend()
                plt.xlabel('Timeline')
                plt.ylabel('Stock')
                plt.title('Value of ' + self.stock_id)
                plt.savefig(self.output_file)
                print("generated:", self.output_file)

            else:
                return json_object['status']['bCodeMessage'][0]['errorMessage']

        return True

if __name__ == '__main__':
    tb = TelegramBot()
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", tb.hello))
    dispatcher.add_handler(CommandHandler("hello", tb.hello))
    dispatcher.add_handler(CommandHandler("predict", tb.predict))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, tb.echo))
    updater.start_polling()
    print('ready for idle...')
    updater.idle()
