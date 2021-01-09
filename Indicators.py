from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator

# Returns the relative strength index for the given data


class RSI:
    wb = None
    time_period = None

    def __init__(self, wb, time_period='m1'):
        self.wb = wb
        self.time_period = time_period

    # Updates the bars
    def get_signal(self, stock):
        rsi_bars = self.wb.get_bars(stock, interval=self.time_period, extendTrading=0, count=14)

        # Initialize RSI
        rsi = RSIIndicator(close=rsi_bars['close'], window=20, fillna=True)
        rsi_series = rsi.rsi()
        current_rsi = rsi_series[13]

        # Make conclusions from data
        if current_rsi <= 30:
            return 1
        elif current_rsi >= 70:
            return -1
        else:
            return 0

# Returns the bollinger band lines for the given data


class BBands:

    wb = None
    time_period = None
    threshold = .15  # percent

    def __init__(self, wb, time_period='m1', threshold=.15):
        self.wb = wb
        self.time_period = time_period
        self.threshold = threshold

    # Updates the bars
    def get_signal(self, stock, minute_price):
        bb_bars = self.wb.get_bars(stock, interval=self.time_period, extendTrading=0, count=20)
        bb = BollingerBands(close=bb_bars['close'], fillna=True)

        # set series objects to indicators calculations
        bb_upper = bb.bollinger_hband()
        bb_lower = bb.bollinger_lband()

        # get value for latest interval
        current_bb_upper = bb_upper[19]
        current_bb_lower = bb_lower[19]

        difference = current_bb_upper - current_bb_lower
        threshold_price = difference * self.threshold
        lower_threshold = current_bb_lower + threshold_price
        upper_threshold = current_bb_upper - threshold_price

        if minute_price <= lower_threshold:
            return 1
        elif minute_price >= upper_threshold:
            return -1
        else:
            return 0
