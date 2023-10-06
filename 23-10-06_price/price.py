from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
from IPython.core.display_functions import display, clear_output
from ipywidgets import FloatSlider, Output, interactive, Dropdown, IntSlider

PRICE_STEP: int = 1


class Trend(Enum):
    increasing = "increasing"
    decreasing = "decreasing"
    null = "null"


class Price:
    def __init__(self, currency: str, value: int):
        self.currency = currency
        self.value = value

    def __str__(self):
        return f"{self.currency}: {self.value}"


class StockPriceSimulator:
    def __init__(self, currency: str = "USD"):
        self.currency = currency

        self.max_price = IntSlider(value=100, min=50, max=150, step=PRICE_STEP, description="Max price")
        self.min_price = IntSlider(value=50, min=0, max=100, step=PRICE_STEP, description="Min price")
        self.interval = IntSlider(value=30, min=20, max=120, step=1, description="Time (s)")
        self.prob = FloatSlider(value=0.5, min=0, max=1, step=0.01, description="Probability")
        self.max_percentage_price_change = FloatSlider(
            value=0.05,
            min=0,
            max=0.2,
            step=0.01,
            description="Max change %"
        )
        self.trend = Dropdown(options=[item.value for item in list(Trend)], description="Trend")
        self.trend_percentage = FloatSlider(value=0.02, min=0, max=0.3, step=0.01, description="Trend %")

        self.interactive_plot = interactive(
            self.update_plot,
            max_price=self.max_price,
            min_price=self.min_price,
            interval=self.interval,
            prob=self.prob,
            max_percentage_price_change=self.max_percentage_price_change,
            trend=self.trend,
            trend_percentage=self.trend_percentage
        )

    def simulate_stock_price(
            self,
            max_price: int,
            min_price: int,
            interval: float,
            prob: float,
            max_percentage_price_change: float,
            trend: str,
            trend_percentage: float
    ) -> list[Price]:
        price = Price(self.currency, (max_price + min_price) / 2)
        price_history = [price]

        for _ in range(1, interval):
            price_value = price.value
            if trend == Trend.increasing.value:
                price_value *= (1 + trend_percentage)
            elif trend == Trend.decreasing.value:
                price_value *= (1 - trend_percentage)

            percentage = np.random.uniform(0, max_percentage_price_change)
            price_value *= (1 + percentage) if np.random.rand() < prob else (1 - percentage)
            price_value = max(min(price_value, max_price), min_price)

            price_history.append(Price(self.currency, price_value))

        return price_history

    @staticmethod
    def _generate_plot(min_price: int, max_price: int, interval: int, prices: list[int]):
        clear_output(wait=True)

        output_plot = Output()
        with output_plot:
            plt.figure(figsize=(10, 6))
            plt.plot(range(interval), prices)
            plt.title("Simulated stock price")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Price")
            plt.ylim(min_price, max_price)
            plt.grid(True)
            plt.show()
        display(output_plot)

    def update_plot(
            self,
            max_price: int,
            min_price: int,
            interval: int,
            prob: float,
            max_percentage_price_change: float,
            trend: str,
            trend_percentage: float
    ) -> None:
        price_history = self.simulate_stock_price(
            max_price,
            min_price,
            interval,
            prob,
            max_percentage_price_change,
            trend,
            trend_percentage
        )
        prices = [price.value for price in price_history]
        self._generate_plot(min_price, max_price, interval, prices)


if __name__ == "__main__":
    simulator = StockPriceSimulator()
    display(simulator.interactive_plot)
