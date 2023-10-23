import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import Output, Input
from dash.dash_table import DataTable

import dom
import layout


class DomDashboard(dom.Dom):
    UPDATE_INTERVAL = 1000

    def __init__(self, depth=20, size=20):
        super().__init__(depth, size)
        self.app = self.create_dash_app()
        self.order = None

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

    def create_dash_app(self):
        app = dash.Dash(__name__, external_stylesheets=[dmc.theme.DEFAULT_COLORS])

        app.layout = layout.dashboard_layout(self.UPDATE_INTERVAL)

        @app.callback(
            [
                Output("dom", "children"),
                Output("order-lock", "children"),
                Output("play-pause", "children")
            ],
            [
                Input("slider-input", "value"),
                Input("play-pause", "n_clicks"),
                Input("update", "n_intervals"),
            ],
        )
        def update_dom(page_size, n_clicks, n_intervals):
            played = n_clicks % 2
            if not played:
                order = self.order
            else:
                order = self.process_order()
            dom_df = self.common_df()
            return [
                self._get_dom_data_table(dom_df, page_size, order),
                self._get_order_lock_data_table(),
                "Play" if not played else "Stop"
            ]

        return app

    def run_dash_app(self, debug: bool = True):
        self.app.run_server(debug=debug)


if __name__ == '__main__':
    dashboard = DomDashboard()
    dashboard.run_dash_app()
