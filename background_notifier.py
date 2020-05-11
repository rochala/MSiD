import simpleaudio
import requests
import json
import time


rising = True


def init(currency, wallet, treshold):
    global rising
    if check_value(currency, wallet) > treshold:
        rising = False
    else:
        rising = True


def start_loop(currency, wallet, treshold):
    global rising
    while True:
        current_price = check_value(currency, wallet)
        if current_price < treshold and not rising:
            rising = True
            notify()
            print(current_price)
        elif current_price > treshold and rising:
            rising = False
            notify()
            print(current_price)
        time.sleep(10)


def notify():
    filename = "daniel_simon.wav"  # created by Daniel's Simon
    wave_obj = simpleaudio.WaveObject.from_wave_file(filename)
    wave_obj.play()


def check_value(currency, wallet):
    try:
        request = requests.get(
            "https://dev-api.shrimpy.io/v1/orderbooks?exchange="
            + f"{wallet['default_market']}&baseSymbol={currency}&"
            + f"quoteSymbol={wallet['default_currency']}&limit=1"
        )
        orderbook = request.json()
        if "error" in orderbook:
            print(orderbook)
        else:
            return float(orderbook[0]["orderBooks"][0]["orderBook"]["bids"][0]["price"])
    except requests.exceptions.RequestException as e:
        print(e)


def start(currency, wallet, treshold):
    init(currency, wallet, treshold)
    notify()
    start_loop(currency, wallet, treshold)
