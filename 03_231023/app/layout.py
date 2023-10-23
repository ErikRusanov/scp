import dash_mantine_components as dmc
from dash.development.base_component import Component


def dashboard_layout() -> Component:
    return dmc.Container([
        dmc.Title("Модель биржевого стакана", mb=32),
        dmc.Grid([
            dmc.Col(id="dom", span=2),
            dmc.Col([
                dmc.Col(id="order_lock"),
                dmc.Slider(
                    value=20,
                    step=2,
                    min=10,
                    max=30,
                    id="slider-input",
                    marks=[
                        {"value": i, "label": i}
                        for i in range(10, 31, 2)
                    ]
                )
            ], span=8
            ),
        ], justify="space-between"
        ),
    ], maw="90%"
    )


def styles_to_dom(best_ask: float, best_bid: float, page_size: int) -> dict:
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
