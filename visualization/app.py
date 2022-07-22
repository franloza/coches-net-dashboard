# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

from model.data_provider import DataProvider
from model import figure_builder

app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
server = app.server

# Provider for the data from DB
data_provider = DataProvider()


def left_panel():
    return dbc.Card(
        body=True,
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
    Output(component_id="query-input", component_property="value"),
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
        "",  # Clear textbox input
    )


@app.callback(
    Output(component_id="x-dropdown", component_property="options"),
    Output(component_id="y-dropdown", component_property="options"),
    Output(component_id="color-dropdown", component_property="options"),
    Input(component_id="vehicle-dropdown", component_property="value"),
)
def update_axis_components(vehicle):
    if vehicle == "motos":
        columns = {
            "price": "Precio",
            "km": "Km",
            "year": "Año",
            "main_province": "Provincia",
            "cubic_capacity": "Cilindrada",
            "fuel_type": "Combustible",
        }
    else:
        columns = {
            "price": "Precio",
            "km": "Km",
            "year": "Año",
            "main_province": "Provincia",
            "cubic_capacity": "Cilindrada",
            "fuel_type": "Combustible",
            "environmental_label": "Etiqueta",
        }
    return columns, columns, columns


@app.callback(
    Output(component_id="table-div", component_property="children"),
    Input(component_id="search-button", component_property="n_clicks"),
    State(component_id="query-input", component_property="value"),
    State(component_id="km-minimum", component_property="value"),
    State(component_id="km-maximum", component_property="value"),
    State(component_id="price-minimum", component_property="value"),
    State(component_id="price-maximum", component_property="value"),
    State(component_id="vehicle-dropdown", component_property="value"),
    State(component_id="fuel-checklist", component_property="value"),
    State(component_id="offer-checklist", component_property="value"),
    State(component_id="province-dropdown", component_property="value"),
    prevent_initial_call=True,
)
def update_table(
    _,
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
    data = data_provider.query_general_data_by_parameters(
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
    return dash_table.DataTable(
        id="data-table",
        columns=[{"name": i, "id": i} for i in data.columns],
        data=data.to_dict("records"),
        page_current=0,
        page_size=10,
        sort_action="native",
        filter_action="native",
        row_selectable="multi",
    )


@app.callback(
    Output(component_id="data-graph", component_property="figure"),
    Input(component_id="data-table", component_property="data"),
    Input(component_id="data-table", component_property="derived_virtual_data"),
    Input(
        component_id="data-table", component_property="derived_virtual_selected_rows"
    ),
    Input(component_id="x-dropdown", component_property="value"),
    Input(component_id="y-dropdown", component_property="value"),
    Input(component_id="color-dropdown", component_property="value"),
    State(component_id="data-graph", component_property="figure"),
    prevent_initial_call=True,
)
def update_figure(data, virtual_data, selected_rows, x, y, color, curr_figure):
    if virtual_data and len(virtual_data) != len(data):
        data = virtual_data

    data = pd.DataFrame.from_records(data)
    return figure_builder.build_general_scatter_figure(
        data, x=x, y=y, color=color, highlight=selected_rows
    )


@app.callback(
    Output(component_id="details-information", component_property="children"),
    Input(
        component_id="data-table", component_property="derived_virtual_selected_rows"
    ),
    State(component_id="data-table", component_property="derived_virtual_data"),
    State(component_id="vehicle-dropdown", component_property="value"),
    prevent_initial_call=True,
)
def show_details(selected_rows, data, vehicle):
    if not selected_rows:
        raise PreventUpdate

    data = pd.DataFrame.from_records(data)
    elements = []
    for _, vehicle_data in data.iloc[selected_rows].iterrows():
        vehicle_id = vehicle_data["motorcycle_id"]
        imgs = data_provider.query_vehicle_resorces("motos", vehicle_id)[0]
        size = min(5, len(imgs))
        price_data = data_provider.get_price_over_time(vehicle, vehicle_id)
        elements.append(
            dbc.Card(
                children=[
                    dbc.Col(
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Carousel(
                                            items=[
                                                {"id": f"{i}", "src": res["url"]}
                                                for i, res in enumerate(imgs[:size])
                                            ],
                                            controls=True,
                                            indicators=True,
                                            variant="dark",
                                        )
                                    ),
                                    dbc.Col(
                                        dcc.Graph(
                                            figure=figure_builder.build_price_timeseries_figura(
                                                price_data
                                            )
                                        ),
                                    ),
                                ],
                                className="g-0 d-flex align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(html.Div(vehicle_data["title"])),
                                    dbc.Col(html.Div(f"Km: {vehicle_data['km']}")),
                                    dbc.Col(html.Div(f"{vehicle_data['price']}€")),
                                    dbc.Col(html.Div(f"{vehicle_data['year']}")),
                                    dbc.Col(html.Div(f"{vehicle_data['fuel_type']}")),
                                    dbc.Col(
                                        html.Div(f"{vehicle_data['main_province']}")
                                    ),
                                ],
                                justify="around",
                            ),
                        ],
                    )
                ]
            )
        )
    return elements


app.layout = dbc.Col(
    children=[
        dbc.Row(
            children=[
                dbc.Col(left_panel(), md=3),
                dbc.Col(
                    md=9,
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
                                html.Div(id="table-div"),
                            ],
                            type="circle",
                        ),
                    ],
                ),
            ],
        ),
        dbc.Container(id="details-information"),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
