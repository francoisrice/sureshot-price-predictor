import sys
from openbb import obb
import numpy as np
import scipy
import os

# Cache stock data for a day
# Add pytest tests


class PricePredictor:
    # Note: Fetched stock data has a daily interval

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

        self.dailyVolatility = stdDev
        self.avgReturn = np.mean(returns)
        self.volatility = stdDev * np.sqrt(252)

    def volatilityIsNone(self):
        return self.volatility == None

    def calculate_drift(self):
        prices = self.stockData.to_list()

        if prices:
            logRate = (np.log(prices[-1] / prices[0])) / len(
                prices
            )  # price change over the available data

            if self.volatilityIsNone():
                self.calculate_volatility()

            self.drift = self.dailyVolatility**2 / 2 + logRate

            # Add Interest rate
            # += fetch_interest_rate()


# 10.  def fetch_interest_rate(): # Needed?
#     return None


def main(args):
    obb.account.login(pat=os.environ["OPENBB_KEY"])
    print(args)
    inputPrice = None
    probability = None

    symbol = args[1]
    if float(args[2]) > 1:
        inputPrice = float(args[2])
    else:
        probability = float(args[2])
    timePeriod = int(args[3])  # DTE (Days to Expiration)

    # pp = PricePredictor("MARA")
    pp = PricePredictor(symbol)

    pp.fetch_stock_data()
    pp.calculate_volatility()
    pp.calculate_drift()

    interestRate = 0.05
    # interestRate = fetch_interest_rate()

    meanEndPrice = pp.currentPrice * (
        (1 + interestRate) ** (timePeriod / 365) * np.exp(pp.drift * timePeriod)
    )
    periodVol = pp.dailyVolatility * np.sqrt(timePeriod)
    if inputPrice:
        # distribution = scipy.stats.norm(meanEndPrice, periodVol)
        # probability = 1 - distribution.cdf(inputPrice)
        zScore = (np.log(inputPrice / meanEndPrice) - pp.avgReturn) / periodVol

        # Percent Chance that price gets above inputPrice
        probability = 1 - scipy.stats.norm.cdf(zScore)
        print(
            str(probability)
            + " Chance that price gets above "
            + str(inputPrice)
            + " in "
            + str(timePeriod)
            + " days."
        )

    elif probability:
        zScoreA = scipy.stats.norm.ppf(1 - probability)
        topPrice = np.exp(zScoreA * periodVol + pp.avgReturn) * meanEndPrice

        zScoreB = scipy.stats.norm.ppf(probability)
        bottomPrice = np.exp(zScoreB * periodVol + pp.avgReturn) * meanEndPrice

        print(
            str(int(probability*100))
            + "% Chance that price gets above "
            + str(topPrice)
            + " or below "
            + str(bottomPrice)
            + " in "
            + str(timePeriod)
            + " days."
        )

    else:
        print("Must provide a price or a percent probability.")


if __name__ == "__main__":
    """
    Usage: python price-predictor.py <symbol> <price|probability> <daysToExpiration>
    
    What's the probability that the price of <symbol> will be above <price> in <daysToExpiration> days?
    What price has a <probability> % chance of being above <price> in <daysToExpiration> days?
    """
    main(sys.argv)
