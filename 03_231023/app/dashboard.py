import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.graph_objs as go
from dash import Output, Input
from dash.dash_table import DataTable

import dom
import layout


class DomDashboard(dom.Dom):
    UPDATE_INTERVAL = 1000

    def __init__(self, depth=20, size=20):
        super().__init__(depth, size)
        self.app = self.create_dash_app()
        self.update = False
        self.restart_clicks = -1

    def _get_dom_data_table(self, dom_df: pd.DataFrame, page_size: int, order: dom.Dom.Order):
        ask_len = len(self.ask)
        rest = page_size // 2

        slice_start = max(ask_len - rest, 0)
        slice_end = min(ask_len + rest, len(dom_df))

        return dmc.Text(str(order or "")), DataTable(
            data=dom_df.iloc[slice_start:slice_end].to_dict("records"),
            **layout.dom_table(self.best_ask, self.best_bid, page_size)
        )

    def _get_order_lock_data_table(self):
        return DataTable(
            data=self.order_lock.to_dict("records"),
            **layout.order_lock_table()
        )

    def _get_best_prices_trace(self):
        bba_trace = list(self.bba_trace)
        timestamps = [bba.get("time") for bba in bba_trace]
        bid = [bba.get("bid") for bba in bba_trace]
        ask = [bba.get("ask") for bba in bba_trace]

        data_bid = go.Scatter(
            x=timestamps,
            y=bid,
            name="Best bid",
            mode='lines+markers'
        )
        data_ask = go.Scatter(
            x=timestamps,
            y=ask,
            name="Best ask",
            mode='lines+markers'
        )
        x_range = [min(timestamps), max(timestamps)] if timestamps else [0, 1]
        y_range = [min(bid) - 5, max(ask) + 5] if timestamps else [0, 1]
        return {
            "data": [data_bid, data_ask],
            "layout": go.Layout(
                xaxis=dict(range=x_range),
                yaxis=dict(range=y_range)
            )
        }

    def create_dash_app(self):
        app = dash.Dash(__name__, external_stylesheets=[dmc.theme.DEFAULT_COLORS])

        app.layout = layout.dashboard_layout(self.UPDATE_INTERVAL)

        @app.callback(
            [
                Output("play-pause", "children"),
                Output("update", "disabled"),
            ],
            [
                Input("play-pause", "n_clicks")
            ]
        )
        def manipulate(n_clicks):
            if not n_clicks % 2:
                self.update = False
                return [
                    "Play",
                    True
                ]

            self.update = True
            return [
                "Stop",
                False
            ]

        @app.callback(
            [
                Output("dom", "children"),
                Output("order-lock", "children"),
                Output("update", "interval"),
                Output("bid-ask-graph", "figure")
            ],
            [
                Input("dom-page-size", "value"),
                Input("update", "n_intervals"),
                Input("intensity", "value"),
                Input("restart", "n_clicks")
            ],
        )
        def update_dom(page_size, n_intervals, intensity, restart_clicks):
            if restart_clicks > self.restart_clicks:
                self.restart_clicks = restart_clicks
                self.restart()
                order = None
            else:
                order = self.process_order() if self.update else None
            dom_df = self.common_df()

            return [
                self._get_dom_data_table(dom_df, page_size, order),
                self._get_order_lock_data_table(),
                (-25 * intensity) // 3 + 1500,
                self._get_best_prices_trace(),
            ]

        return app

    def run_dash_app(self, debug: bool = True):
        self.app.run_server(debug=debug)


if __name__ == '__main__':
    dashboard = DomDashboard()
    dashboard.run_dash_app()
