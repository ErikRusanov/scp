import time

import numpy as np
import pandas as pd

DATA_FILE = "../data/order_log_20231006150822.csv"

current_bid = {}
current_ask = {}
bb_ba_history = {}
start = time.time()

df = pd.read_csv(DATA_FILE)

filtered_data = df[(df['sess_id'] == 6899) & (df['isin_id'] == 3032021)]

prices = np.array(filtered_data['price'])
amounts = np.array(filtered_data['amount'])
timestamps = np.array(filtered_data['moment_ns'])
directions = np.array(filtered_data['dir'])
actions = np.array(filtered_data['action'])

best_bid = -1
best_ask = -1

for i in range(len(filtered_data)):
    price = prices[i]
    amount = amounts[i]
    timestamp = timestamps[i]
    direction = directions[i]
    action = actions[i]

    if direction == 1:
        if action == 1:
            best_bid = max(best_bid, price)
            current_bid[price] = current_bid.get(price, 0) + amount
        elif action in (2, 0):
            current_bid[price] -= amount
            if current_bid[price] == 0:
                del current_bid[price]
                best_bid = max(current_bid, default=-1)
    else:
        if action == 1:
            best_ask = min(best_ask, price) if best_ask != -1 else price
            current_ask[price] = current_ask.get(price, 0) + amount
        elif action in (2, 0):
            current_ask[price] -= amount
            if current_ask[price] == 0:
                del current_ask[price]
                best_ask = min(current_ask, default=-1)

    bb_ba_history[timestamp] = {"best_ask": best_ask, "best_bid": best_bid}
