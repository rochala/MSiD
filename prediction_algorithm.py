import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from random import randrange
import requests as req

norm = {}


def fetch_data(currency, startTime, endTime):
    limit = min(1000, int((endTime - startTime) / 86400 + 1))
    data = req.get(
        "https://www.bitstamp.net/api/v2/ohlc/{0}/".format(currency),
        params={
            "start": startTime - 86400,
            "end": endTime,
            "step": 86400,
            "limit": limit,
        },
    )
    return data.json()


def parse_data(data):
    global norm
    df = pd.DataFrame.from_records(data["data"]["ohlc"])
    df.set_index("timestamp", inplace=True)
    df = df.apply(pd.to_numeric, errors="coerce")
    df["ratio"] = df["close"] / df["volume"]
    norm = {
        "close": [df["close"].min(), df["close"].max()],
        "volume": [df["volume"].min(), df["volume"].max()],
        "ratio": [df["ratio"].min(), df["ratio"].max()],
    }
    df["close"] = (df["close"] - df["close"].min()) / (
        df["close"].max() - df["close"].min()
    )
    df["volume"] = (df["volume"] - df["volume"].min()) / (
        df["volume"].max() - df["volume"].min()
    )
    df["ratio"] = (df["ratio"] - df["ratio"].min()) / (
        df["ratio"].max() - df["ratio"].min()
    )
    df["price_diff"] = df["close"].diff()
    df["volume_diff"] = df["volume"].diff()
    return df


def denormalize(value):
    price = value[0] * (norm["close"][1] - norm["close"][0]) + norm["close"][0]
    volume = value[1] * (norm["volume"][1] - norm["volume"][0]) + norm["volume"][0]
    return [price, volume]


def normalize(value):
    price = (value[0] - norm["close"][0]) / (norm["close"][1] - norm["close"][0])
    volume = (value[1] - norm["volume"][0]) / (norm["volume"][1] - norm["volume"][0])
    return [price, volume]


def calc_ratio(value):
    value_denormalized = denormalize(value)
    ratio = value_denormalized[0] / value_denormalized[1]
    ratio = (ratio - norm["ratio"][0]) / (norm["ratio"][1] - norm["ratio"][0])
    return ratio


def predict_next_day(last_value, knn):
    next_day = knn.predict(last_value)
    previous_day = last_value[0][:2]
    diffs = []
    diffs.append(next_day[0][0] - previous_day[0])
    diffs.append(next_day[0][1] - previous_day[1])
    diffs.append(calc_ratio([next_day[0][0], next_day[0][1]]))
    next_day = np.append(next_day, diffs)
    return np.reshape(next_day, (-1, 1)).T


def plot(y_test, y_, y_future, title):
    fig, ax1 = plt.subplots(figsize=(30, 10))

    y_denorm = np.apply_along_axis(denormalize, 1, y_)
    y_test_denorm = np.apply_along_axis(denormalize, 1, y_test)

    ax1.plot(
        np.arange(len(y_denorm)), y_denorm[:, [0]], color="navy", label="predictionTest"
    )
    ax1.plot(
        np.arange(len(y_test_denorm)),
        y_test_denorm[:, [0]],
        color="orange",
        label="realValue",
    )
    ax1.plot(
        range(len(y_denorm), len(y_denorm) + len(y_future)),
        np.array(y_future)[:, [0]],
        color="green",
        label="predictionFutur",
    )
    ax1.plot(
        [len(y_denorm) - 1, len(y_denorm)],
        [y_denorm[-1, [0]], np.array(y_future)[0, [0]]],
        color="green",
    )
    ax2 = ax1.twinx()
    ax2.set_xlabel("date")
    ax2.set_ylabel("volume")
    ax2.tick_params(axis="y")

    ax2.bar(
        np.arange(len(y_denorm)),
        np.array(y_denorm[:, [1]]).ravel(),
        alpha=0.5,
        width=0.3,
    )
    ax2.bar(
        range(len(y_denorm), len(y_denorm) + len(y_future)),
        np.array(y_future)[:, [1]].ravel(),
        alpha=0.5,
        width=0.3,
    )
    ax2.bar(0, 25e10, alpha=0)

    plt.axis("tight")
    ax1.legend()
    plt.title(title)
    plt.show()


def future_values(next_days, X_val, knn):
    y_sim = []
    next_day_value = predict_next_day(X_val, knn)
    y_sim.append(denormalize(next_day_value.tolist()[0][:2]))

    for i in range(0, next_days):
        next_day_value = predict_next_day(next_day_value, knn)
        y_sim.append(denormalize(next_day_value.tolist()[0][:2]))

    return y_sim


def simulate(iterations, neighbors, future_predictions, currency, start, end):
    # data split
    data = fetch_data(currency, start, end)
    df = parse_data(data)

    X = np.array(df[["close", "volume", "price_diff", "volume_diff", "ratio"]])[1:]
    y = np.array(df[["close", "volume"]])[1:]

    random = randrange(100000000)

    knn = KNeighborsRegressor(neighbors)
    knn.fit(X, y)

    y_ = knn.predict(X[-int(1 - len(y) * 0.8) :])

    mse = mean_squared_error(y[-int(1 - len(y) * 0.8) :], y_)
    mae = mean_absolute_error(y[-int(1 - len(y) * 0.8) :], y_)

    y_future = np.array(future_values(future_predictions, X[[-1]], knn))

    plot(
        y[-int(1 - len(y) * 0.8) :],
        y_,
        y_future,
        "Real prices 1 simulation without noise",
    )

    y_mean = y_
    y_test_mean = y[-int(1 - len(y) * 0.8) :]

    print(
        f"Mean squared error: {mse}   Mean absolute error:{mae}   Random seed: {random}"
    )
    print(
        f"Mean Close: {np.mean(y_future, axis=(0))[0]}  Mean Volume: {np.mean(y_future, axis=(0))[1]}\n"
        + f"Median Close: {np.median(y_future, axis=(0))[0]}  Median Volume: {np.mean(y_future, axis=(0))[1]}\n"
        + f"Std Close: {np.std(y_future, axis=(0))[0]}  Std Volume: {np.mean(y_future, axis=(0))[1]}\n"
    )

    mse = 0
    mae = 0
    print("\n")

    for i in range(0, iterations - 1):

        # Reset

        X_train = X[: int(len(X) * 0.8)]
        X_test = X[: int(1 - len(X) * 0.8)]
        y_train = y[: int(len(y) * 0.8)]
        y_test = y[: int(1 - len(y) * 0.8)]

        # Noise

        X_train += X_train * np.random.normal(0, 0.02, size=(len(X_train), 5))
        X_test += X_test * np.random.normal(0, 0.02, size=(len(X_test), 5))
        y_train += y_train * np.random.normal(0, 0.02, size=(len(y_train), 2))
        y_test += y_test * np.random.normal(0, 0.02, size=(len(y_test), 2))

        knn.fit(X_train, y_train)
        y_ = knn.predict(X_test)

        mse += mean_squared_error(y_test, y_)
        mae += mean_absolute_error(y_test, y_)

        y_mean += y_
        y_test_mean += y_test
        y_future += np.array(future_values(future_predictions, X_test[[-1]], knn))

    y_mean /= iterations
    y_test_mean /= iterations
    y_future /= iterations

    print(
        f"Mean squared error: {mse/iterations}   Mean absolute error:{mae/iterations}"
    )
    plot(
        y_mean, y_test_mean, y_future, "Mean prices from 100 simulations with noise",
    )
    print(
        f"Mean Close: {np.mean(y_future, axis=(0))[0]}  Mean Volume: {np.mean(y_future, axis=(0))[1]}\n"
        + f"Median Close: {np.median(y_future, axis=(0))[0]}  Median Volume: {np.mean(y_future, axis=(0))[1]}\n"
        + f"Std Close: {np.std(y_future, axis=(0))[0]}  Std Volume: {np.mean(y_future, axis=(0))[1]}\n"
    )


# simulate(neighbors, iterations, days for prediction, currency <btcusd>, timestamp start, timestamp end)
if __name__ == "__main__":
    simulate(8, 100, 10, "ethusd", 1551705072, 1591705072)
