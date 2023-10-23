from collections import deque
from datetime import datetime
from enum import Enum
from typing import Callable

import numpy as np
import pandas as pd
from pydantic import BaseModel


class Dom:
    price_distribution: Callable = np.random.normal
    price_distribution_kwargs: dict = {
        "loc": 100,
        "scale": 10
    }

    class Order(BaseModel):
        class Type(Enum):
            limit: str = "Limit"
            market: str = "Market"

        class Action(Enum):
            buy: str = "Buy"
            sell: str = "Sell"

        price: float
        type: Type
        action: Action
        amount: int

        def __init__(self, *, price: float = None, amount: int = None, **kwargs):
            _price = price or round(Dom.price_distribution(**Dom.price_distribution_kwargs))
            _amount = amount or np.random.randint(5, 15)

            super().__init__(price=_price, amount=_amount, **kwargs)

        def to_dict(self) -> dict:
            return {
                key: value if not isinstance(value, Enum) else value.value
                for key, value in self.model_dump().items()
            }

        def __str__(self):
            return (f"{self.action.value.upper()} {self.type.value.upper()} order "
                    f"with price = {self.price}, amount = {self.amount}")

    def __init__(
            self,
            depth: int = 20,
            size: int = 20
    ):
        self.size = size
        self.depth = depth
        self.bid = pd.DataFrame(columns=["price", "orders"])
        self.ask = pd.DataFrame(columns=["price", "orders"])
        self.order_lock = pd.DataFrame(columns=["price", "type", "action", "amount", "time"])
        self.bba_trace = deque(maxlen=20)

        self._generate_bid(size)
        self._generate_ask(size)

    def __str__(self):
        sorted_bid = self.bid.sort_values(by='price', ascending=False)
        sorted_ask = self.ask.sort_values(by='price')

        _bid = "======== BID ========"

        for index, row in sorted_bid.iterrows():
            _bid += f"\nPrice {row['price']}. Amounts:"
            for order in row['orders']:
                _bid += f" {order.amount} |"

        _ask = "======== ASK ======="
        for index, row in sorted_ask.iterrows():
            _ask += f"\nPrice {row['price']}. Amounts:"
            for order in row['orders']:
                _ask += f" {order.amount} |"

        return "\n\n".join([_bid, _ask])

    def restart(self):
        self.ask = self.ask.drop(self.ask.index)
        self.bid = self.bid.drop(self.bid.index)
        self.order_lock = self.order_lock.drop(self.order_lock.index)
        self.bba_trace = deque(maxlen=20)

        self._generate_bid(self.size)
        self._generate_ask(self.size)

    @property
    def best_bid(self) -> float:
        if not self.bid.empty:
            return self.bid["price"].max()
        return 0.

    @property
    def best_ask(self) -> float:
        if not self.ask.empty:
            return self.ask["price"].min()
        return float("inf")

    @property
    def best_ask_orders(self) -> list[Order]:
        return self.ask[self.ask["price"] == self.best_ask]["orders"].values[0]

    @property
    def best_bid_orders(self) -> list[Order]:
        return self.bid[self.bid["price"] == self.best_bid]["orders"].values[0]

    def _add_order_to_bid(self, order: Order) -> None:
        price = order.price

        if price in self.bid["price"].values:
            index = self.bid.index[self.bid["price"] == price][0]
            self.bid.at[index, "orders"].append(order)
        else:
            self.bid = pd.concat(
                [
                    self.bid.dropna(axis=1, how="all"), pd.DataFrame({"price": [price], "orders": [list()]})
                ],
                ignore_index=True
            )
            self.bid.at[self.bid.index[-1], "orders"].append(order)

    def _add_order_to_ask(self, order: Order) -> None:
        price = order.price

        if price in self.ask["price"].values:
            index = self.ask.index[self.ask["price"] == price][0]
            self.ask.at[index, "orders"].append(order)
        else:
            self.ask = pd.concat(
                [
                    self.ask.dropna(axis=1, how="all"), pd.DataFrame({"price": [price], "orders": [list()]})
                ],
                ignore_index=True
            )
            self.ask.at[self.ask.index[-1], "orders"].append(order)

    def _update_order_lock(self, order: Order) -> None:
        self.order_lock = pd.concat(
            [
                pd.DataFrame([order.to_dict() | {"time": (time := datetime.now())}]),
                self.order_lock.dropna(axis=1, how="all"),
            ],
            ignore_index=True
        )

    def _generate_bid(self, size: int) -> None:
        for _ in range(size):
            order = self.Order(type=self.Order.Type.limit, action=self.Order.Action.buy)
            self._add_order_to_bid(order)

    def _generate_ask(self, size: int) -> None:
        orders_len = 0
        best_bid = self.best_bid
        while orders_len < size:
            if (order := self.Order(type=self.Order.Type.limit, action=self.Order.Action.sell)).price < best_bid:
                continue
            self._add_order_to_ask(order)
            orders_len += 1

    def _random_order(self) -> Order:
        order_action = np.random.choice(list(self.Order.Action))
        order_type = np.random.choice(list(self.Order.Type))

        if order_action == self.Order.Action.buy:
            best_ask = self.best_ask
            if order_type == self.Order.Type.limit:
                while (order := self.Order(action=order_action, type=order_type)).price > best_ask:
                    continue
            else:
                order = self.Order(action=order_action, type=order_type, price=best_ask)
        else:
            best_bid = self.best_bid
            if order_type == self.Order.Type.limit:
                while (order := self.Order(action=order_action, type=order_type)).price < best_bid:
                    continue
            else:
                order = self.Order(action=order_action, type=order_type, price=best_bid)
        return order

    def _execute_market(self, order: Order, best_price_orders: list[Order] = None) -> None:
        best_price_orders = best_price_orders or (
            self.best_bid_orders
            if order.action == self.Order.Action.sell
            else self.best_ask_orders
        )

        deal_order = best_price_orders[0]
        deal_amount = min(deal_order.amount, order.amount)
        deal_order.amount -= deal_amount

        self._update_order_lock(order)
        order.amount -= deal_amount

        if not deal_order.amount:
            best_price_orders.remove(deal_order)

        if best_price_orders:
            if not order.amount:
                return
            return self._execute_market(order, best_price_orders)

        if order.action == self.Order.Action.sell:
            self.bid = self.bid[self.bid["price"] != self.best_bid]
            if not order.amount:
                return
            return self._execute_market(order, self.best_bid_orders)
        else:
            self.ask = self.ask[self.ask["price"] != self.best_ask]
            if not order.amount:
                return
            return self._execute_market(order, self.best_ask_orders)

    def _execute_limit(self, order: Order) -> None:
        if order.action == self.Order.Action.sell:
            if order.price == self.best_bid:
                return self._execute_market(order)

            return self._add_order_to_ask(order)
        else:
            if order.price == self.best_ask:
                return self._execute_market(order)

            return self._add_order_to_bid(order)

    def common_df(self) -> pd.DataFrame:
        sorted_bid = self.bid.rename(columns={"orders": "bid"})
        sorted_ask = self.ask.rename(columns={"orders": "ask"})

        common_df = pd.merge(sorted_bid, sorted_ask, on="price", how="outer")

        common_df["bid"].fillna(0, inplace=True)
        common_df["ask"].fillna(0, inplace=True)

        common_df["bid"] = common_df["bid"].apply(lambda x: sum(o.amount for o in x) if not isinstance(x, int) else x)
        common_df["ask"] = common_df["ask"].apply(lambda x: sum(o.amount for o in x) if not isinstance(x, int) else x)

        common_df["bid"] = common_df["bid"].apply(lambda x: "-" if x == 0 else x)
        common_df["ask"] = common_df["ask"].apply(lambda x: "-" if x == 0 else x)

        common_df = common_df[["bid", "price", "ask"]]
        return common_df.sort_values(by="price", ascending=False)

    def process_order(self) -> Order:
        order = self._random_order()
        initial_amount = order.amount

        self.bba_trace.append({"time": datetime.now().timestamp(), "bid": self.best_bid, "ask": self.best_ask})

        if order.type == self.Order.Type.limit:
            self._execute_limit(order)
        else:
            self._execute_market(order)

        order.amount = initial_amount
        return order
