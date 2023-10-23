import dash_mantine_components as dmc
from dash import dcc
from dash.development.base_component import Component


def dashboard_layout(update_interval: int) -> Component:
    return dmc.Container([
        dmc.Title("Depth of Market", mb=32),
        dmc.Grid([
            dmc.Col(id="dom", span=2),
            dmc.Col([
                dmc.Grid(
                    [
                        dmc.Col(
                            dmc.Slider(
                                value=20,
                                step=2,
                                min=10,
                                max=30,
                                id="dom-page-size",
                                marks=[
                                    {"value": i, "label": i}
                                    for i in range(10, 31, 2)
                                ],
                            ),
                            span=5
                        ),
                        dmc.Col(
                            dmc.Slider(
                                value=90,
                                min=10,
                                max=170,
                                id="intensity",
                                marks=[
                                    {"value": i, "label": i}
                                    for i in [10, 90, 170]
                                ],
                            ),
                            span=4
                        ),
                        dmc.Col(
                            dmc.Button(children="Play", id="play-pause", n_clicks=0),
                            span=1
                        ),
                        dmc.Col(
                            dmc.Button(children="Restart", id="restart", n_clicks=0),
                            span=1
                        )
                    ],
                    mb=32,
                    justify="space-between"
                ),
                dmc.Grid(
                    [
                        dmc.Col(
                            dcc.Graph(id="bid-ask-graph", animate=True),
                        ),
                        dmc.Col(id="order-lock"),
                    ]
                ),
            ], span=9
            ),
        ], justify="space-between"
        ),
        dcc.Interval(id="update", interval=update_interval, n_intervals=0, disabled=False)
    ], maw="90%"
    )


def dom_table(best_ask: float, best_bid: float, page_size: int) -> dict:
    extra_filter = {
        "if": {
            "filter_query": f'{{price}} = {best_ask}',
            "column_id": "price"
        },
        "backgroundColor": "#FAAD61",
    } if best_bid == best_ask else {}

    return {
        "page_size": page_size,
        "columns": [
            {"name": "bid", "id": "bid"},
            {"name": "price", "id": "price"},
            {"name": "ask", "id": "ask"},
        ],
        "style_table": {"padding": "12px"},
        "style_cell": {"textAlign": "center", "backgroundColor": "#edede9"},
        "style_data_conditional": [
            {
                "if": {
                    "filter_query": "{bid} != '-'",
                    "column_id": "bid"
                },
                "backgroundColor": "#51a051"
            },
            {
                "if": {
                    "column_id": "price"
                },
                "backgroundColor": "#e8ebe4",
            },
            {
                "if": {
                    "filter_query": f'{{price}} = {best_ask}',
                    "column_id": "price"
                },
                "backgroundColor": "#FF4136",
                "color": "#fff"
            },
            {
                "if": {
                    "filter_query": f'{{price}} = {best_bid}',
                    "column_id": "price"
                },
                "backgroundColor": "#0A5F38",
                "color": "#fff"
            },
            extra_filter,
            {
                "if": {
                    "filter_query": "{ask} != '-'",
                    "column_id": "ask"
                },
                "backgroundColor": "#ff6b6b"
            }
        ]
    }


def order_lock_table() -> dict:
    return {
        "columns": [
            {"name": "price", "id": "price"},
            {"name": "type", "id": "type"},
            {"name": "action", "id": "action"},
            {"name": "amount", "id": "amount"},
            {"name": "time", "id": "time"},
        ],
        "page_size": 12
    }
