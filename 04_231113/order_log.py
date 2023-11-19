import ipywidgets as widgets
import numpy as np
import pandas as pd
import plotly.express as px
from IPython.core.display_functions import display as ipy_display
from IPython.display import clear_output
from ipywidgets import Output


class OrderLog:
    def __init__(self, data):
        self.data = data
        self.isin_id_dropdown = widgets.Dropdown(options=self.get_unique_values(data, 'isin_id'),
                                                 description='ISIN ID:')
        self.sess_id_dropdown = widgets.Dropdown(options=self.get_unique_values(data, 'sess_id'),
                                                 description='Session ID:')
        self.build_button = widgets.Button(description='Build Chart')

        self.output_plot = Output()

        # Link button click event
        self.build_button.on_click(self.on_button_click)

        # Display widgets
        ipy_display(self.isin_id_dropdown, self.sess_id_dropdown, self.build_button, self.output_plot)

    @staticmethod
    def read_data(data_file):
        return pd.read_csv(data_file)

    @staticmethod
    def get_unique_values(df, column):
        return df[column].unique()

    @staticmethod
    def filter_data(df, isin_id, sess_id):
        return df[(df['sess_id'] == sess_id) & (df['isin_id'] == isin_id)]

    @staticmethod
    def process_data(filtered_data):
        current_bid = {}
        current_ask = {}
        bb_ba_history = {}

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

        return zip(*((stamp, entry.get("best_ask"), entry.get("best_bid")) for stamp, entry in bb_ba_history.items()))

    def on_button_click(self, b):
        isin_id = self.isin_id_dropdown.value
        sess_id = self.sess_id_dropdown.value

        filtered_data = self.filter_data(self.data, isin_id, sess_id)
        timestamps, ba, bb = self.process_data(filtered_data)

        with self.output_plot:
            clear_output(wait=True)
            fig = px.line(
                x=timestamps,
                y=[bb, ba],
                title='Order Log',
                line_shape='linear',
                template='plotly',
                line_dash_sequence=['solid', 'solid'],
                color_discrete_sequence=['green', 'red'],
                labels={'best_bid': 'Best Bid', 'best_ask': 'Best Ask'}
            )
            fig.show()


# Read data when starting the app
data_file_path = "../data/order_log_20231006150822.csv"  # Adjust the path accordingly
order_log = OrderLog(OrderLog.read_data(data_file_path))
