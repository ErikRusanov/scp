from collections import deque
from enum import Enum

import numpy as np
from IPython.core.display_functions import display
from ipywidgets import Output
from matplotlib import pyplot as plt
from pydantic import BaseModel


class OrderAction(Enum):
    buy: str = "купить"
    sell: str = "продать"


class OrderType(Enum):
    market: str = "market"
    limit: str = "limit"


class Order(BaseModel):
    symbol: str
    action: OrderAction
    type: OrderType
    quantity: int
    price: int

    @staticmethod
    def generate_data(symbol: str = "BTC") -> dict:
        _action = np.random.choice([a for a in OrderAction], p=[0.5, 0.5])
        _type = np.random.choice([t for t in OrderType], p=[0.5, 0.5])
        _quantity = int(np.random.normal(10, 4))
        _price = int(np.random.normal(100, 10))
        return {
            "symbol": symbol,
            "action": _action,
            "type": _type,
            "quantity": _quantity,
            "price": _price,
        }


class OrderBookForSymbol(BaseModel):
    symbol: str = "BTC"
    buy: deque[Order] = deque()
    sell: deque[Order] = deque()

    def display_book(self):
        buy_prices = [order.price for order in self.buy]
        sell_prices = [order.price for order in self.sell]
        buy_quantities = [order.quantity for order in self.buy]
        sell_quantities = [order.quantity for order in self.sell]
        output_plot = Output()
        with output_plot:
            fig, ax = plt.subplots(figsize=(10, 5))

            ax.barh(buy_prices, buy_quantities, color='g', alpha=0.7, label='Buy Orders')
            ax.barh(sell_prices, sell_quantities, color='r', alpha=0.7, label='Sell Orders')

            ax.set_xlabel('Quantity')
            ax.set_ylabel('Price')
            ax.set_title(f"Order Book for {self.symbol}")
            ax.legend()

            plt.tight_layout()
            plt.show()

        display(output_plot)


if __name__ == "__main__":
    order_book = OrderBookForSymbol()

    for _ in range(5):
        order_book.buy.append(Order(**Order.generate_data()))

    for _ in range(5):
        order_book.sell.append(Order(**Order.generate_data()))

    order_book.display_book()
