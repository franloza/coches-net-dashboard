# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px

from model.data_provider import DataProvider
from model import figure_builder

app = Dash(__name__)

# Provider of the data from DB
data_provider = DataProvider()


def left_panel():
    return html.Div(
        style={"float": "left"},
        children=[
            dcc.Input(id="query-input"),
            html.Div(
                children=[
                    html.Label("KM"),
                    dcc.Input(value=0, type="number", id="km-minumum", min=0),
                    dcc.Input(value=100000, type="number", id="km-maximum", min=0),
                ]
            ),
            dcc.Dropdown(
                {"coches": "Coches", "motos": "Motos"}, "motos", id="vehicle-dropdown"
            ),
            html.Label("Fuel Type"),
            dcc.Checklist(
                {
                    "Gasolina": "Gasolina",
                    "Diesel": "Diesel",
                    "Hibrido": "Hibrido",
                    "plug-in hybrid": "Plug-in Hybrid",
                    "Eléctrico": "Eléctrico",
                },
                ["Gasolina", "Diesel", "Hibrido", "plug-in hybrid", "Eléctrico"],
                id="fuel-checklist",
            ),
            html.Label("Offer Type"),
            dcc.Checklist(
                {
                    "new": "New",
                    "km0": "Km0",
                    "used": "Used",
                },
                ["new", "km0", "used"],
                id="offer-checklist",
            ),
            html.Button("Search", id="search-button"),
        ],
    )


@app.callback(
    Output(component_id="x-dropdown", component_property="options"),
    Output(component_id="y-dropdown", component_property="options"),
    Output(component_id="color-dropdown", component_property="options"),
    Input(component_id="vehicle-dropdown", component_property="value"),
)
def update_axis_componenet(vehicle):
    if vehicle == "motos":
        columns = {
            "price": "Precio",
            "km": "Km",
            "year": "Año",
            "mainProvince": "Provincia",
        }
    else:
        raise NotImplementedError("coches dimension columns not yet specified")
    return columns, columns, columns


@app.callback(
    Output(component_id="example-graph", component_property="figure"),
    Input(component_id="search-button", component_property="n_clicks"),
    Input(component_id="x-dropdown", component_property="value"),
    Input(component_id="y-dropdown", component_property="value"),
    Input(component_id="color-dropdown", component_property="value"),
    State(component_id="query-input", component_property="value"),
    State(component_id="km-minumum", component_property="value"),
    State(component_id="km-maximum", component_property="value"),
    State(component_id="vehicle-dropdown", component_property="value"),
    State(component_id="fuel-checklist", component_property="value"),
    State(component_id="offer-checklist", component_property="value"),
)
def update_output_div(_, x, y, color, title, km_min, km_max, vehicle, fuel, offer):
    data = data_provider.query_data_by_parameters(
        title=title,
        km_min=km_min,
        km_max=km_max,
        vehicle=vehicle,
        fuel=fuel,
        offer=offer,
    )
    return figure_builder.build_price_distribution_figure(data, x=x, y=y, color=color)


app.layout = html.Div(
    style={"width": "100%"},
    children=[
        left_panel(),
        html.Div(
            style={"float": "right", "width": "80%", "margin": "auto"},
            children=[
                dcc.Loading(
                    children=[
                        dcc.Dropdown(id="x-dropdown", value="price"),
                        dcc.Dropdown(id="y-dropdown", value="km"),
                        dcc.Dropdown(id="color-dropdown", value="year"),
                        dcc.Graph(id="example-graph"),
                    ],
                    type="circle",
                ),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
