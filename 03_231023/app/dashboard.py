from enum import Enum

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

    def _get_dom_data_table(self, dom_df: pd.DataFrame, page_size: int) -> DataTable:
        ask_len = len(self.ask)
        rest = page_size // 2

        slice_start = max(ask_len - rest, 0)
        slice_end = min(ask_len + rest, len(dom_df))

        return DataTable(
            data=dom_df.iloc[slice_start:slice_end].to_dict("records"),
            **layout.styles_to_dom(self.best_ask, self.best_bid, page_size)
        )

    def _get_order_lock_data_table(self) -> DataTable:
        return DataTable(
            data=pd.DataFrame(
                [
                    {key: value if not isinstance(value, Enum) else value.value for key, value in order.items()}
                    for order in self.order_lock
                ]
            ).to_dict("records"),
            columns=[
                {"name": "price", "id": "price"},
                {"name": "type", "id": "type"},
                {"name": "action", "id": "action"},
                {"name": "amount", "id": "amount"},
            ],
            page_size=12
        )

    def create_dash_app(self):
        app = dash.Dash(__name__, external_stylesheets=[dmc.theme.DEFAULT_COLORS])

        app.layout = layout.dashboard_layout()

        @app.callback(
            [
                Output("dom", "children"),
                Output("order_lock", "children")
            ],
            Input("slider-input", "value")
        )
        def update_dom(page_size):
            self.process_order()
            dom_df = self.common_df()
            return [
                self._get_dom_data_table(dom_df, page_size),
                self._get_order_lock_data_table()
            ]

        return app

    def run_dash_app(self, debug: bool = True):
        self.app.run_server(debug=debug)


if __name__ == '__main__':
    dashboard = DomDashboard()
    dashboard.run_dash_app()
