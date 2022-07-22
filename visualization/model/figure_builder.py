# Module with auxiliary functions to return figures from a data_provider dataframe
import pandas as pd
import plotly.express as px


def build_general_scatter_figure(
    data: pd.DataFrame, x: str, y: str, color: str = None, highlight: list = None
):
    """Returns a figure with the price distributions of the elements in `data`.
    `data` must have the columns `["km", "price"]`

    Args:
        data (pd.DataFrame): DF with the data to plot. must have the columns `["km", "price"]`.
        x (str): Column to use as x axis.
        y (str): Column to use as y axis.
        color (str): If provided, it will add an aditional dimension the plot in form of color.
        highlight (list[int]): If provided, highlights by size the rows provided in the list (row index)
    """
    if not {"km", "price"}.issubset(data.columns):
        raise ValueError("Required columns `km` and `price` are missing in the data.")
    if color and color not in data.columns:
        raise ValueError(f"Provided dimensioned {color} not found inside the data.")
    if data.empty:
        return {}  # Empty plot

    return px.scatter(
        data,
        x=x,
        y=y,
        color=color,
        trendline="ols",
        marginal_x="box",
        size=[0.1 if _ not in highlight else 0.75 for _ in range(len(data))]
        if highlight is not None and highlight
        else None,
        hover_data=["id", "price", "km", "year"],
    )


def build_price_timeseries_figura(data):
    """Returns a timeseries line chart with the prices over time.

    Args:
        data (pd.DataFrame): Data to plot. Must contain the columns `date_key` and `price`
    """
    if not {"date_key", "price"}.issubset(data.columns):
        raise ValueError(
            "Required columns `date_key` and `price` are missing in the data."
        )
    return px.line(data, x="date_key", y="price", markers="o")
