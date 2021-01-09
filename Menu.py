from webull import paper_webull
from AutoTrader import WebullAlgoTrader
import threading
import sys
import getpass

# The main menu for the algo trader. accepts commands to control the trader.


class Menu:
    wb = None  # Webull object
    trading = False
    trader = None  # object of WebullAlgoTrader. Created after login is successful.
    commands = ['trade', 'stop', 'pause', 'resume', 'commands', 'view stock list', 'add stock list',
                'remove stock list', 'view realtime', 'pause realtime', 'performance']
    stock_list = ['TSLA', 'SPY', 'NIO', 'PSTH', 'ICLN', 'BA', 'AAPL', 'PLTR', 'GME', 'AMZN', 'PLUG', 'RIOT', 'TWTR',
                  'FB', 'ARKG', 'BABA', 'MARA', 'ARKK', 'NVDA']

    def __init__(self):
        print('Hello and welcome to Webull Algo Trader.')
        print('Only Paper trading is supported at the moment due to experimental results.')
        print('Please login to begin and type the command \'trade\'')
        print('To see all other commands type the command \'command\'')
        self.wb = paper_webull()
        self.attempt_login(1)
        self.await_command()

    # Awaits commands to be entered to control the algo trader. The thread that runs the trading is seperate from the
    # command thread
    def await_command(self):
        command = input()
        if command == 'trade':
            if not self.trading:
                t = threading.Thread(target=self.trade())
        elif command == 'pause':
            print('Pausing')
        elif command == 'resume':
            print('Resuming')
        elif command == 'stop':
            print('Stopping')
            sys.exit()
        elif command == 'commands':
            for c in self.commands:
                print(c)
        elif command == 'view stock list':
            for stock in self.stock_list:
                print(stock)
        elif command == 'add stock list':
            print('add')
        elif command == 'remove stock list':
            print('remove')
        elif command == 'view realtime':
            print('view')
        elif command == 'pause realtime':
            print('un view')
        self.await_command()

    # Attempts login using username, password and usually multi factor authentication
    def attempt_login(self, attempt):
        username = input('Enter Webull email: ')
        password = getpass.getpass('Enter Webull password: ')
        logged_in = False

        # Try logging in with just username and password
        try:
            self.wb.login(username, password)
            self.wb.get_account_id()
            logged_in = True

        # Login failed
        except:
            print('Invalid email or password, or multi-factor authentication required.')

            # Try getting a multi-factor authentication
            try:
                self.wb.get_mfa(username)

                # If MFA fails, try logging in again
                try:
                    mfa = input('Enter multi-factor authentication: ')
                    self.wb.login(username, password, mfa)
                    self.wb.get_account_id()
                    logged_in = True
                except:
                    print('Password or multi-factor-authentication are incorrect.')
                    print('Try again.')
            except:
                print('MFA attempted; invalid username')
        finally:
            if not logged_in:
                if attempt == 5:
                    sys.exit()
                print('Login failed, attempt number ' + attempt + ' of 5')
                self.attempt_login(attempt + 1)
            else:
                print('Login successful')
                self.trader = WebullAlgoTrader(self.wb, 'd1', refresh_rate=30)
                self.trader.set_stock_list(self.stock_list)

    def trade(self):
        self.trader.start_trading()

    def set_stock_list(self):
        self.trader.set_stock_list(self.stock_list)