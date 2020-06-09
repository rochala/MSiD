import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from random import randrange


# load training data
df = pd.read_csv("btcdata.csv", header=0)
df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y%m%d")
df.head()
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


df.set_index("timestamp", inplace=True)
df.sort_values(["timestamp"], ascending=False)
df.head()


# data prep
X = np.array(df[["close", "volume", "price_diff", "volume_diff", "ratio"]])[1:-1]
y = np.array(df[["close", "volume"]])[2:]


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


def simulate(iterations, neighbors, future_predictions):
    # data split
    random = randrange(100000000)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.10, random_state=random
    )

    knn = KNeighborsRegressor(neighbors)
    knn.fit(X_train, y_train)

    y_ = knn.predict(X_test)

    mse = mean_squared_error(y_test, y_)
    mae = mean_absolute_error(y_test, y_)

    y_future = np.array(future_values(future_predictions, X[[-1]], knn))

    plot(y_test, y_, y_future)

    y_mean = y_
    y_test_mean = y_test

    print(
        f"Mean squared error: {mse}   Mean absolute error:{mae}   Random seed: {random}"
    )

    mse = 0
    mae = 0

    for i in range(0, iterations - 1):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.10)

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
    plot(y_mean, y_test_mean, y_future)
    print(
        f"Mean Close: {np.mean(y_future, axis=(0))[0]}  Mean Volume: {np.mean(y_future, axis=(0))[1]}\n"
        + f"Median Close: {np.median(y_future, axis=(0))[0]}  Median Volume: {np.mean(y_future, axis=(0))[1]}\n"
        + f"Std Close: {np.std(y_future, axis=(0))[0]}  Std Volume: {np.mean(y_future, axis=(0))[1]}\n"
    )


def simulate(iterations, neighbors, future_predictions):
    # data split
    random = randrange(100000000)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=random
    )

    knn = KNeighborsRegressor(neighbors)
    knn.fit(X, y)

    y_ = knn.predict(X[-len(y_test) :])

    mse = mean_squared_error(y[-len(y_test) :], y_)
    mae = mean_absolute_error(y[-len(y_test) :], y_)

    y_future = np.array(future_values(future_predictions, X[[-1]], knn))

    plot(
        y[-len(y_test) :],
        y_,
        y_future,
        "Real prices 1 simulation without randomizing arrays",
    )

    y_mean = y_
    y_test_mean = y[-len(y_test) :]

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
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

        # knn.fit(X_train, y_train)
        y_ = knn.predict(X_test)

        mse += mean_squared_error(y_test, y_)
        mae += mean_absolute_error(y_test, y_)

        y_mean += y_
        y_test_mean += y_test
        y_future += np.array(future_values(future_predictions, X[[-1]], knn))

    y_mean /= iterations
    y_test_mean /= iterations
    y_future /= iterations

    print(
        f"Mean squared error: {mse/iterations}   Mean absolute error:{mae/iterations}"
    )

    plot(
        y_mean,
        y_test_mean,
        y_future,
        "Mean prices from 100 simulations with randomizing arrays",
    )
    print(
        f"Mean Close: {np.mean(y_future, axis=(0))[0]}  Mean Volume: {np.mean(y_future, axis=(0))[1]}\n"
        + f"Median Close: {np.median(y_future, axis=(0))[0]}  Median Volume: {np.mean(y_future, axis=(0))[1]}\n"
        + f"Std Close: {np.std(y_future, axis=(0))[0]}  Std Volume: {np.mean(y_future, axis=(0))[1]}\n"
    )


if __name__ == "__main__":
    simulate(8, 100, 10)
