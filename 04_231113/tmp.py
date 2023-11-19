DATA_FILE = "tmp.csv"
current_bid: dict = {}
current_ask: dict = {}
bb_ba_history: dict = {}

with open(DATA_FILE) as f:
    for line in f.readlines()[1:]:
        split_line = line.split(",")
        amount, price, timestamp, direction, action = (
            int(split_line[4]), split_line[8], split_line[11],
            int(split_line[12]), int(split_line[13])
        )
        best_bid = sorted(current_bid.keys())[-1] if current_bid else "-1"
        best_ask = sorted(current_ask.keys())[0] if current_ask else "-1"

        if direction == 1:
            if action == 1:
                if price > best_bid:
                    best_bid = price
                current_price_amount = current_bid.get(price, 0)
                current_bid[price] = current_price_amount + amount

            elif action == 2:
                current_bid[price] -= amount
                if current_bid[price] == 0:
                    current_bid.pop(price)
                    best_bid = sorted(current_bid.keys())[-1] if current_bid else "-1"

            elif action == 0:
                current_bid[price] -= amount

        else:
            if action == 1:
                if best_ask != -1 and price < best_ask:
                    best_ask = price
                current_price_amount = current_ask.get(price, 0)
                current_ask[price] = current_price_amount + amount

            elif action == 2:
                current_ask[price] -= amount
                if current_ask[price] == 0:
                    current_ask.pop(price)
                    best_ask = sorted(current_ask.keys())[0] if current_ask else "-1"

            elif action == 0:
                current_ask[price] -= amount

        bb_ba_history[timestamp] = {"best_ask": best_ask, "best_bid": best_bid, "price": price, "direction": direction}

    for key, value in bb_ba_history.items():
        best_bid, best_ask = value.get("best_bid"), value.get("best_ask")
        print(
            f"{key}: BEST_BID = {best_bid} | BEST_ASK = {best_ask} > "
            f"price = {value.get('price')}, direction = {value.get('direction')}",
            end=" "
        )

        if best_bid > best_ask:
            print(f"!!!!!", end="")
        print()
