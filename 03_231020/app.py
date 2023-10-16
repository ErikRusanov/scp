import dash_mantine_components as dmc
import pandas as pd
from dash import Dash, callback, Input, Output
from dash.dash_table import DataTable

df = pd.read_csv("order_lock.csv")
dom = pd.read_csv("dom.csv")

app = Dash("DOM", external_stylesheets=[dmc.theme.DEFAULT_COLORS])
app.layout = dmc.Container([
    dmc.Title("Модель биржевого стакана", mb=32),
    dmc.Grid([
        dmc.Col(id="dom", span=2),
        dmc.Col([
            DataTable(
                data=df.to_dict("records"),
                page_size=10,
                style_table={"padding": "12px", "radius": "10px"}
            ),
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


@callback(Output("dom", "children"), Input("slider-input", "value"))
def update_dom_size(value):
    print()
    # print(dom.values)
    slice_start = max((len(dom) - value) // 2, 0)
    slice_end = min((len(dom) + value) // 2, len(dom))
    return DataTable(
        data=dom.iloc[slice_start:slice_end].to_dict("records"),
        page_size=value,
        columns=[
            {"name": "bid", "id": "bid"},
            {"name": "price", "id": "price"},
            {"name": "ask", "id": "ask"},
        ],
        style_table={"padding": "12px"},
        style_cell={"textAlign": "center", "backgroundColor": "#edede9"},
        style_data_conditional=[
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
                    "filter_query": f'{{price}} = {dom[dom["bid"] != "-"].iloc[0]["price"]}',
                    "column_id": "price"
                },
                "backgroundColor": "#0A5F38",
                "color": "#fff"
            },
            {
                "if": {
                    "filter_query": f'{{price}} = {dom[dom["ask"] != "-"].iloc[-1]["price"]}',
                    "column_id": "price"
                },
                "backgroundColor": "#FF4136",
            },
            {
                "if": {
                    "filter_query": "{ask} != '-'",
                    "column_id": "ask"
                },
                "backgroundColor": "#ff6b6b"
            }
        ]
    )


if __name__ == '__main__':
    app.run(debug=True)
