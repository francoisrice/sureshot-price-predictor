import sys
from openbb import obb
import numpy as np
import os

# Cache stock data for a day
# Add pytest tests


class PricePredictor:
    # Note: Fetched stock data has a daily interval

    obb.account.login(pat=os.environ["OPENBB_KEY"])

    def __init__(self, symbol="") -> None:
        self.symbol = symbol

    def fetch_stock_data(self, symbol="") -> None:
        if symbol:
            self.symbol = symbol
        stockDataFrame = obb.equity.price.historical(
            symbol=self.symbol,
            start_date=None,
            interval="1d",
            include_actions=False,
            provider="yfinance",
        ).to_df()

        # Calc Median prices for the each timeframe
        stockDataFrame["avgPrice"] = (
            stockDataFrame["high"] + stockDataFrame["low"] + stockDataFrame["close"]
        ) / 3

        self.stockData = stockDataFrame["avgPrice"]
        self.currentPrice = stockDataFrame["close"].iloc[-1]

    def calculate_volatility(self) -> None:
        # Daily volatility over the last 21 trading days, annualized

        # prices = self.stockData["avgPrice"]
        prices = self.stockData.to_list()

        if not prices:
            self.fetch_stock_data()
            # prices = self.stockData["avgPrice"]
            prices = self.stockData.to_list()

        returns = [
            np.log(prices[index + 1] / prices[index])
            for index in range(len(prices) - 1)
        ]

        stdDev = np.std(returns)

        self.volatility = stdDev * np.sqrt(252)

    def volatilityIsNone(self):
        return self.volatility == None

    def calculate_drift(self):
        prices = self.stockData.to_list()

        if prices:
            if len(prices) > 21:
                logRate = (
                    np.log(prices[-1] / prices[-21])
                ) / 21  # price change in the last month
            else:
                logRate = (np.log(prices[-1] / prices[0])) / len(
                    prices
                )  # price change over the available data

            if self.volatilityIsNone():
                self.calculate_volatility()

            self.drift = self.volatility**2 / 2 + logRate

            # Add Interest rate
            # += fetch_interest_rate()


# 10.  def fetch_interest_rate(): # Needed?
#     return None


def main(args):
    print(args)
    symbol = args[1]
    if float(args[2]) > 0:
        inputPrice = float(args[2])
    else:
        probability = float(args[2])

    # pp = PricePredictor("MARA")
    pp = PricePredictor(symbol)

    pp.fetch_stock_data()
    pp.calculate_volatility()
    pp.calculate_drift()

    interestRate = 0.05
    # interestRate = fetch_interest_rate()

    # calculate_mean_price()
    # calculate_drift()
    # calculate_volatility() -> std_dev

    # Probability is probability based on std dev input price is away from mean price, factoring in drift
    if inputPrice:
        # Calculate probability of price being above inputPrice
        zScore = (inputPrice - pp.currentPrice) / pp.volatility
        probability = 1 - np.exp(-zScore)
        print(probability)
    elif probability:
        # Calculate prices based on probability
        zScore = -np.log(1 - probability)
        inputPrice = pp.currentPrice + zScore * pp.volatility
        print(inputPrice)
    else:
        print("Must provide a price or a percent probability.")


if __name__ == "__main__":
    """
    Usage: python price-predictor.py <symbol> <price|probability>
    """
    main(sys.argv)
