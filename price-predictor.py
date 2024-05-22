from openbb import obb
import numpy as np
import os


class PricePredictor:
    # Note: Fetched stock data has a daily interval

    obb.account.login(pat=os.environ["OPENBB_KEY"])

    def __init__(self, symbol="") -> None:
        self.symbol = symbol

    def fetch_stock_data(self, symbol="") -> None:
        stockDataFrame = obb.equity.price.historical(
            symbol,
            start_date=None,
            interval="1d",
            include_actions=False,
            provider="yfinance",
        ).to_df()

        # Calc Median prices for the each timeframe
        # avgPrice = (high + low + close) / 3

        # self.stockData = [timestamps,avgPrices]

    # 1.
    def calculate_volatility(self) -> None:
        # Daily volatility over the last 21 trading days, annualized
        # self.stockData

        returns = [
            np.log(avgPrices[index + 1] / avgPrices[index])
            for index in range(len(avgPrices) - 1)
        ]

        stdDev = np.std(returns)

        self.volatility = stdDev * np.sqrt(252)

    def volatilityIsNone(self):
        return self.volatility == None

    # 2.
    def calculate_drift(self):

        logRate = 0
        # logRate = (np.log(data[-1]) - np.log(data[0])) / timePeriod
        # logRate = (np.log(stockData[-1]) - np.log(stockData[0])) / (timestamp[-1] - timestamp[0])

        if self.volatilityIsNone():
            self.calculate_volatility()

        self.drift = self.volatility**2 / 2 + logRate

        # Add Interest rate
        # += fetch_interest_rate()


# 10.  def fetch_interest_rate(): # Needed?
#     return None

# 9. def fetch_current_price():
#     return None


def main():
    currentPrice = 10

    pp = PricePredictor("MARA")

    # calculate_mean_price()
    # calculate_drift()
    # calculate_volatility() -> std_dev

    # Probability is probability based on std dev input price is away from mean price, factoring in drift

    print("Hello World!")


if __name__ == "__main__":
    main()
