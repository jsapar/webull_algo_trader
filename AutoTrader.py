from Indicators import BBands
from Indicators import RSI
import threading
import time
import math

# Algorithmic stock trader based on two technical indicators. Default time period is set to one day and refreshed every
# 30 minutes. The algorithm uses all of the paper money it can to buy as many shares of a BUY stock it can. Then when it
# get a sell signal, it will sell all shares.


class WebullAlgoTrader:
    trading = None
    wb = None
    time_period = None
    refresh_rate = None  # minutes

    login_refresh_thread = None
    login_refresh_rate = 30 # minutes
    stock_list = None

    def __init__(self, user, time_period='m5', refresh_rate=5):
        self.trading = False
        self.time_period = time_period
        self.refresh_rate = refresh_rate
        self.wb = user
        self. login_refresh_thread = threading.Thread(target=self.login_refresh_function)
        self.login_refresh_thread.start()

    def start_trading(self):
        self.trading = True

        bb = BBands(wb=self.wb, time_period=self.time_period)
        rsi = RSI(wb=self.wb, time_period=self.time_period)

        while self.trading:
            for stock in self.stock_list:

                has_position = self.has_position(stock)

                # Get analysis of rsi and bb for the stock; 1 = buy; -1 = sell; 0 = hold
                rsi_signal = rsi.get_signal(stock)
                bb_signal = bb.get_signal(stock, self.get_avg_minute_price(stock))

                price = self.get_avg_minute_price(stock)

                # Determine what to do with your position
                if bb_signal + rsi_signal == 2:
                    print(time.strftime("%H:%M:%S", time.localtime()) + ' ' + stock + ': Buy\n')
                    if not has_position:
                        self.cancel_orders(stock)
                        self.wb.place_order(stock=stock, action='BUY', orderType='LMT', price=price, enforce='DAY', quant=self.get_max_shares(stock))
                elif bb_signal + rsi_signal == -2:
                    print(time.strftime("%H:%M:%S", time.localtime()) + ' ' + stock + ': Sell\n')
                    if has_position:
                        self.cancel_orders(stock)
                        print(self.wb.place_order(stock=stock, action='SELL', orderType='LMT', price=price,  enforce='DAY', quant=self.get_position(stock)))
                else:

                    print(time.strftime("%H:%M:%S", time.localtime()) + ' ' + stock + ': Hold\n')

                # Wait for X amount of seconds
            time.sleep(self.refresh_rate * 60)

    def stop_trading(self):
        self.trading = False
        print('Trading stopped. Logging out of Webull')
        self.wb.logout()
        print('Logged out.')

    def get_position(self, ticker):
        for position in self.wb.get_account()['positions']:
            if position['ticker']['symbol'] == ticker:
                return int(position['position'])
        return 0

    def has_position(self, ticker):
        for position in self.wb.get_positions():
            if position['ticker']['symbol'] == ticker:
                return True
        return False

    def get_avg_minute_price(self, ticker):
        bars = self.wb.get_bars(ticker, interval='m1', extendTrading=0, count=1)
        return round(bars['high'][0] + bars['low'][0] / 2, 1)

    def get_usable_cash(self):
        return int(float(self.wb.get_account()['accountMembers'][1]['value']))

    def get_total_market_value(self):
        return int(self.wb.get_account()['accountMembers']['totalMarketValue'])

    def get_max_shares(self, stock):
        cash = self.get_usable_cash()
        price = self.get_avg_minute_price(stock)
        return math.trunc(cash/price)

    def cancel_orders(self, stock):
        for order in self.wb.get_current_orders():
            if order['ticker']['symbol'] == stock:
                self.wb.cancel_order(order['orderId'])

    def set_stock_list(self, stock_list):
        self.stock_list = stock_list

    # Should only be called in its own dedicated thread
    def login_refresh_function(self):
        time.sleep(60 * self.login_refresh_rate)
        if self.trading:
            self.wb.refresh_login()
            print('Login refreshed.')
        else:
            self.wb.logout()
            print('Trading has stopped but login refresh attempted; logging out.')
