import requests
import time
import configparser


offers = {}
apis = {}
currencies = {}
fees = {}
wallet = 1000


def load_config():
    global apis, currencies
    config = configparser.RawConfigParser()
    config.read("config.ini")
    apis = config.items("api")
    currencies = config.items("currencies")


def run_algorithm():
    global offers
    for currency in currencies:
        offers = {}
        if fetch_data(currency[1]):
            update_wallet(currency[1])
        else:
            print("Couldn't finish fetching data")
        time.sleep(24)  # public api limit mitiagion


def fetch_data(currency):
    for i in range(len(apis)):
        if not update_trade(i, currency):
            return False
    return True


def update_trade(api_index, currency):
    try:
        request = requests.get(
            "https://dev-api.shrimpy.io/v1/orderbooks?exchange="
            + f"{apis[api_index][1]}&baseSymbol={currency}&quoteSymbol=USD&limit=1"
        )
        trades = request.json()
        if "error" not in trades:
            offers[api_index] = (
                trades[0]["orderBooks"][0]["orderBook"]["asks"][0],
                trades[0]["orderBooks"][0]["orderBook"]["bids"][0],
            )
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        offers[api_index] = None
        print(e)


def update_wallet(currency):
    global wallet
    (best_buy_index, best_sell_index) = get_best_trades()
    result = calculate_profit(best_buy_index, best_sell_index)
    if result[1] > 0:
        wallet += result[1]
        print(
            f"Bought {result[0]:>.5f} of {currency} "
            + f"with rate of {offers[best_buy_index][0]['price']} "
            + f"from {apis[best_buy_index][1]} "
            + f"and sold it at {apis[best_sell_index][1]} "
            + f"with rate of {offers[best_sell_index][1]['price']} "
            + f"with total profit of {result[1]:>.4f} USD"
        )
    else:
        print("Unprofitable transaction")


def calculate_profit(best_buy_index, best_sell_index):
    global wallet
    quantity = float(
        min(
            offers[best_buy_index][0]["quantity"],
            offers[best_sell_index][1]["quantity"],
        )
    )
    max_quantity = wallet / float(offers[best_buy_index][0]["price"])
    if quantity > max_quantity:
        quantity = max_quantity
    profit = float(offers[best_sell_index][1]["price"]) - float(
        offers[best_buy_index][0]["price"]
    )
    profit *= float(quantity)
    return (quantity, float(profit))


def get_best_trades():
    best_buy_index = 0
    best_sell_index = 0
    for i in range(1, len(apis)):
        if offers[i][0]["price"] < offers[best_buy_index][0]["price"]:
            best_buy_index = i
        if offers[i][1]["price"] > offers[best_sell_index][1]["price"]:
            best_sell_index = i
    return (best_buy_index, best_sell_index)


def apply_fee():
    for i in range(len(apis)):
        offers[i][0]["price"] = float(offers[i][0]["price"]) * (fees[i] + 1)
        offers[i][1]["price"] = float(offers[i][1]["price"]) * (1 - fees[i])


def fetch_fee():
    try:
        request = requests.get("https://dev-api.shrimpy.io/v1/list_exchanges")
        unparsed_fees = request.json()
        for i in range(len(apis)):
            for market in unparsed_fees:
                if market["exchange"] == apis[i][1]:
                    fees[i] = market["worstCaseFee"]
    except requests.exceptions.RequestException as e:
        print(e)


def main():
    global wallet
    load_config()
    fetch_fee()
    while True:
        run_algorithm()
        print(f"Wallet is worth {wallet} USD")


main()
