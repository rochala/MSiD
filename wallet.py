import argparse
import sys
import requests
import json
import background_notifier


def add(currency, ammount):
    wallet = load()
    if estimate_price(currency, ammount, wallet) > 0:
        if currency in wallet["currencies"]:
            wallet["currencies"][currency] += ammount
        else:
            wallet["currencies"][currency] = ammount
    else:
        print("Unsupported currency")
    save(wallet)


def remove(currency, ammount):
    wallet = load()
    if estimate_price(currency, ammount, wallet) > 0:
        if wallet["currencies"][currency] <= ammount:
            del wallet["currencies"][currency]
            print(wallet)
        else:
            wallet["currencies"][currency] -= ammount
    else:
        print("Unsupported currency")
    save(wallet)


def change_ammount(currency, ammount):
    wallet = load()
    if estimate_price(currency, ammount, wallet) > 0:
        if currency in wallet["currencies"]:
            wallet["currencies"][currency] = ammount
        else:
            wallet["currencies"][currency] = ammount
    else:
        print("Unsupported currency")
    save(wallet)


def set_default_currency(currency):
    wallet = load()
    wallet["default_currency"] = currency
    save(wallet)


def set_default_market(market):  # check if market exists
    wallet = load()
    try:
        request = requests.get("https://dev-api.shrimpy.io/v1/list_exchanges")
        market_list = request.json()
        if "error" in market_list:
            print("Limit reached")
        else:
            if sum(map(lambda x: market.lower() in x["exchange"], market_list)) > 0:
                wallet["default_market"] = market
                save(wallet)
        if wallet["default_market"] != market.lower():
            print("Unsupported market. Try another one.")
    except requests.exceptions.RequestException as e:
        print(e)


def turn_notifier(currency, treshold):
    wallet = load()
    background_notifier.start(currency, wallet, treshold)


def check_price(wallet):
    prices = {}
    for currency in wallet["currencies"].items():
        prices[currency[0]] = estimate_price(currency[0], currency[1], wallet)
    return prices


def estimate_price(currency, ammount, wallet):
    markets = ["CoinbasePro", "Gemini", "Bittrex", "BinanceUs"]
    estimated_ammount = 0
    try:
        request = requests.get(
            "https://dev-api.shrimpy.io/v1/orderbooks?exchange="
            + f"{wallet['default_market']}&baseSymbol={currency}&"
            + f"quoteSymbol={wallet['default_currency']}&limit=25"
        )
        orderbook = request.json()
        if "error" in orderbook:
            print(orderbook)
        i = 0
        while orderbook[0]["orderBooks"][0]["orderBook"] is None and i < len(markets):
            request = requests.get(
                "https://dev-api.shrimpy.io/v1/orderbooks?exchange="
                + f"{markets[i]}&baseSymbol={currency}&"
                + f"quoteSymbol={wallet['default_currency']}&limit=25"
            )
            orderbook = request.json()
            i += 1
        if orderbook[0]["orderBooks"][0]["orderBook"] is None:
            return -1
        else:
            currency_value = 0
            i = 0
            while estimated_ammount < ammount and i < 25:
                offer = orderbook[0]["orderBooks"][0]["orderBook"]["bids"][i]
                i += 1
                if float(offer["quantity"]) > ammount - estimated_ammount:
                    currency_value += float(offer["price"]) * (
                        ammount - estimated_ammount
                    )
                    estimated_ammount = ammount
                else:
                    currency_value += float(offer["price"]) * float(offer["quantity"])
                    estimated_ammount += float(offer["quantity"])
            if estimated_ammount < ammount:
                averange_price = currency_value / estimated_ammount
                currency_value += averange_price * (ammount - estimated_ammount)
            return currency_value

    except requests.exceptions.RequestException as e:
        print(e)


def print_wallet():
    wallet = load()
    price = check_price(wallet)
    print(
        f"Default currency: {wallet['default_currency']:<15}Default market: {wallet['default_market']}"
    )
    print(
        f"{'    Currency':<15}|{'   Quantity':<15}|{' Average price':<15}|{' Total price':<15}"
    )
    print("---------------------------------------------------------------")
    for currency in wallet["currencies"].items():
        averange_price = float(price[currency[0]]) / float(currency[1])
        print(
            f"{currency[0]:>15}|{currency[1]:>15.6f}|{averange_price:>15.5f}|{price[currency[0]]:>15.5f}"
        )


def save(wallet):
    with open("wallet.json", "w") as json_file:
        json.dump(wallet, json_file)


def load():
    with open("wallet.json") as json_file:
        return json.load(json_file)


def main():
    parser = argparse.ArgumentParser(
        description="Cryptocurrency wallet with basic operations and price notifier."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="Show current wallet values for all currencies",
    )
    group.add_argument(
        "-a",
        "--add",
        nargs=2,
        required=False,
        help="Add new currency to wallet (Cryptocurrency code, ammount) STRING FLOAT",
    )
    group.add_argument(
        "-r",
        "--remove",
        nargs=2,
        required=False,
        help="Remove existing currency to wallet (Cryptocurrency code, ammount) STRING FLOAT",
    )
    group.add_argument(
        "-s",
        "--set",
        nargs=2,
        required=False,
        help="Set currency to wallet (Cryptocurrency code, ammount) STRING FLOAT",
    )
    group.add_argument(
        "-n",
        "--notifier",
        nargs=2,
        required=False,
        help="Start notifying currency (Cryptocurrency code, treshold) STRING FLOAT",
    )

    group.add_argument("--default_market", help="Set default market STRING")
    group.add_argument(
        "--default_currency", help="Set default currency (Cryptocurrency code) STRING"
    )

    args = parser.parse_args()
    if len(sys.argv) == 1:
        print_wallet()
    elif args.list is True:
        print_wallet()
    elif args.add is not None:
        if type(args.add[0]) is str and type(float(args.add[1])) is float:
            add(str(args.add[0]).upper(), float(args.add[1]))
        else:
            print(
                "wallet.py: error: argument -a/-add: expected 2 arguments of type (string, float)"
            )
    elif args.remove is not None:
        if type(args.remove[0]) is str and type(float(args.remove[1])) is float:
            remove(str(args.remove[0]).upper(), float(args.remove[1]))
        else:
            print(
                "wallet.py: error: argument -r/-remove: expected 2 arguments of type (string, float)"
            )
    elif args.set is not None:
        if type(args.set[0]) is str and type(float(args.set[1])) is float:
            change_ammount(str(args.set[0]).upper(), float(args.set[1]))
        else:
            print(
                "wallet.py: error: argument -s/-set: expected 2 arguments of type (string, float)"
            )
    elif args.notifier is not None:
        if type(args.notifier[0]) is str and type(float(args.notifier[1])) is float:
            turn_notifier(str(args.notifier[0]).upper(), float(args.notifier[1]))
        else:
            print(
                "wallet.py: error: argument -n/-notifier: expected 2 arguments of type (string, float)"
            )
    elif args.default_market is not None:
        if type(args.default_market[0]) is str:
            set_default_market(args.default_market)
        else:
            print(
                "wallet.py: error: argument --default_market: expected 1 arguments of type string"
            )
    elif args.default_currency is not None:
        if type(args.default_currency[0]) is str:
            set_default_currency(str(args.default_currency).upper())
        else:
            print(
                "wallet.py: error: argument --default_currency: expected 1 arguments of type string"
            )


main()
