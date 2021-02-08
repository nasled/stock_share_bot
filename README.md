# Telegram Stock Share Bot

Bot allows to parse Nasdaq's index symbol data and predict stock share value using linear regression model. 

Useful for initial market analysis.

Commands
* /hello - welcome message
* /predict STOCK_ID START_YEAR  - load default configuration

Example
```
/predict SENS
/predict SENS 2012
/predict SENS 2020
```

Deploy
```
git clone https://github.com/nasled/stock_share_bot.git
cd stock_share_bot
pip install -r requirements.txt
```

Config 
* update TELEGRAM_BOT_TOKEN

Run
```
chmod 0777 regression_chart.png
chmod +x regression_chart.py
regression_chart.py
```

[Wiki](https://en.wikipedia.org/wiki/Linear_regression)