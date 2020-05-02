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
        print(currency)
        fetch_data(currency[1])
        time.sleep(24)  # public api limit mitiagion


def fetch_data(currency):
    error_flag = False
    for i in range(0, 4):
        if not update_trade(i, currency):
            error_flag = True
    if not error_flag:
        update_wallet(currency)
    else:
        print("Couldn't finish fetching data")


def update_trade(api_index, currency):
    try:
        request = requests.get(
            "https://dev-api.shrimpy.io/v1/orderbooks?exchange="
            + f"{apis[api_index][1]}&baseSymbol={currency}&quoteSymbol=USD&limit=1"
        )
        trades = request.json()
        if "error" not in trades:
            print(trades[0]["orderBooks"][0]["orderBook"]["asks"][0]["price"])
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
    result = calculate_profit()
    if result["sell"][2] > 0:
        wallet += result["sell"][2]
        print(
            f'Bought {result["buy"][0]} of {currency} '
            + f"with rate of {result['buy'][1]} "
            + f"from {result['buy'][2]} "
            + f"and sold it at {result['sell'][0]} "
            + f"with rate of {result['sell'][1]} "
            + f"with total profit of {result['sell'][2]:>.4f} USD"
        )
    else:
        print("Unprofitable transaction")


def calculate_profit():
    global wallet
    (best_buy_value, best_sell_value) = get_best_trades()
    quantity = float(min(best_buy_value[0]["quantity"], best_sell_value[0]["quantity"]))
    max_quantity = wallet / float(best_buy_value[0]["price"])
    if quantity > max_quantity:
        quantity = max_quantity
    profit = float(best_sell_value[0]["price"]) - float(best_buy_value[0]["price"])
    profit *= float(quantity)
    return {
        "buy": (quantity, best_buy_value[0]["price"], apis[best_buy_value[1]][1],),
        "sell": (
            apis[best_sell_value[1]][1],
            best_sell_value[0]["price"],
            float(profit),
        ),
    }


def get_best_trades():
    best_buy_value = (offers[0][0], 0)
    best_sell_value = (offers[0][1], 0)
    for i in range(1, 4):
        if offers[i][0]["price"] < best_buy_value[0]["price"]:
            best_buy_value = (offers[i][0], i)
        if offers[i][1]["price"] > best_sell_value[0]["price"]:
            best_sell_value = (offers[i][1], i)
    return (best_buy_value, best_sell_value)


def apply_fee():
    for i in range(0, 4):
        offers[i][0]["price"] = float(offers[i][0]["price"]) * (fees[i] + 1)
        offers[i][1]["price"] = float(offers[i][1]["price"]) * (1 - fees[i])


def fetch_fee():
    try:
        request = requests.get("https://dev-api.shrimpy.io/v1/list_exchanges")
        unparsed_fees = request.json()
        for i in range(0, 4):
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
