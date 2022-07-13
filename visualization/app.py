# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from calendar import c
from dash import Dash, html, dcc, Input, Output, State, dash_table
import plotly.express as px

from model.data_provider import DataProvider
from model import figure_builder

app = Dash(__name__)

# Provider for the data from DB
data_provider = DataProvider()


def left_panel():
    return html.Div(
        style={"float": "left"},
        children=[
            dcc.Input(id="query-input"),
            html.Div(
                children=[
                    html.Label("KM"),
                    dcc.Input(value=0, type="number", id="km-minimum", min=0),
                    dcc.Input(value=100000, type="number", id="km-maximum", min=0),
                ]
            ),
            html.Div(
                children=[
                    html.Label("Price"),
                    dcc.Input(value=0, type="number", id="price-minimum", min=0),
                    dcc.Input(value=100000, type="number", id="price-maximum", min=0),
                ]
            ),
            dcc.Dropdown(
                {"coches": "Coches", "motos": "Motos"}, "motos", id="vehicle-dropdown"
            ),
            html.Label("Fuel Type"),
            dcc.Checklist(
                id="fuel-checklist",
            ),
            html.Label("Offer Type"),
            dcc.Checklist(
                id="offer-checklist",
            ),
            html.Label("Main Province"),
            dcc.Dropdown(id="province-dropdown", multi=True, searchable=True),
            html.Button("Search", id="search-button"),
        ],
    )


@app.callback(
    Output(component_id="fuel-checklist", component_property="options"),
    Output(component_id="fuel-checklist", component_property="value"),
    Output(component_id="offer-checklist", component_property="options"),
    Output(component_id="offer-checklist", component_property="value"),
    Output(component_id="province-dropdown", component_property="options"),
    Output(component_id="province-dropdown", component_property="value"),
    Input(component_id="vehicle-dropdown", component_property="value"),
)
def populate_filters(vehicle):
    # Common filters
    fuel_checklist = data_provider.query_fuel_types(vehicle)
    offer_checklist = data_provider.query_offer_types(vehicle)
    province_dropdown = data_provider.query_provinces(vehicle)

    return (
        fuel_checklist,
        fuel_checklist,
        offer_checklist,
        offer_checklist,
        province_dropdown,
        province_dropdown,
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
    Output(component_id="data-graph", component_property="figure"),
    Output(component_id="data-table", component_property="columns"),
    Output(component_id="data-table", component_property="data"),
    Input(component_id="search-button", component_property="n_clicks"),
    Input(component_id="x-dropdown", component_property="value"),
    Input(component_id="y-dropdown", component_property="value"),
    Input(component_id="color-dropdown", component_property="value"),
    State(component_id="query-input", component_property="value"),
    State(component_id="km-minimum", component_property="value"),
    State(component_id="km-maximum", component_property="value"),
    State(component_id="price-minimum", component_property="value"),
    State(component_id="price-maximum", component_property="value"),
    State(component_id="vehicle-dropdown", component_property="value"),
    State(component_id="fuel-checklist", component_property="value"),
    State(component_id="offer-checklist", component_property="value"),
    State(component_id="province-dropdown", component_property="value"),
)
def update_output_div(
    _,
    x,
    y,
    color,
    title,
    km_min,
    km_max,
    price_min,
    price_max,
    vehicle,
    fuel,
    offer,
    provinces,
):
    data = data_provider.query_data_by_parameters(
        title=title,
        km_min=km_min,
        km_max=km_max,
        price_min=price_min,
        price_max=price_max,
        vehicle=vehicle,
        fuel=fuel,
        offer=offer,
        provinces=provinces,
    )
    return (
        figure_builder.build_price_distribution_figure(data, x=x, y=y, color=color),
        [{"name": i, "id": i} for i in data.columns],
        data.to_dict("records"),
    )


app.layout = html.Div(
    style={"width": "100%"},
    children=[
        left_panel(),
        html.Div(
            style={"float": "right", "width": "80%", "margin": "auto"},
            children=[
                dcc.Loading(
                    children=[
                        html.Div(
                            style={"display": "inline"},
                            children=[
                                dcc.Dropdown(
                                    id="x-dropdown",
                                    value="price",
                                ),
                                dcc.Dropdown(
                                    id="y-dropdown",
                                    value="km",
                                ),
                                dcc.Dropdown(
                                    id="color-dropdown",
                                    value="year",
                                ),
                            ],
                        ),
                        dcc.Graph(id="data-graph"),
                        dash_table.DataTable(
                            id="data-table",
                            page_current=0,
                            page_size=10,
                        ),
                    ],
                    type="circle",
                ),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
