import requests
import argparse
import time
from sys import exit


trades = None


def update_trades(crypto_currency, currency):
    global trades
    try:
        request = requests.get(
            f"https://bitbay.net/API/Public/{crypto_currency}{currency}/orderbook.json"
        )
        trades = request.json()
    except requests.exceptions.RequestException as e:
        trades = None
        print(e)


def print_trades(lines):
    for i in range(0, lines):
        bid = trades["bids"][i][0]
        ask = trades["asks"][i][0]
        print(f"{bid:>-10}    {ask:>-10}    {((ask - bid) / bid):>-.4f}%")


def analysis(crypto_currency, currency, delay, lines):
    update_trades(crypto_currency, currency)
    if trades is not None:
        print_trades(lines)
        print("\n")
    try:
        for i in range(delay):
            time.sleep(1)
    except KeyboardInterrupt:
        exit(0)
    return analysis(crypto_currency, currency, delay, lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cryptocurrency")
    parser.add_argument("currency")
    parser.add_argument("-d", "--delay", type=int, choices=range(1, 61))
    parser.add_argument("-n", "--lines", type=int, choices=range(1, 26))
    args = parser.parse_args()
    if args.delay is not None and args.lines is not None:
        analysis(args.cryptocurrency, args.currency, args.delay, args.lines)
    elif args.delay is not None:
        analysis(args.cryptocurrency, args.currency, args.delay, 10)
    elif args.lines is not None:
        analysis(args.cryptocurrency, args.currency, 5, args.lines)
    else:
        analysis(args.cryptocurrency, args.currency, 5, 10)


main()
