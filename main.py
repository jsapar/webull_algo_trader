import threading
from Menu import Menu


def thread_function():
    menu = Menu()

# Initializes the program then starts the menu thread.


if __name__ == '__main__':
    t = threading.Thread(target=thread_function)
    t.start()

