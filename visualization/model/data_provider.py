from contextlib import contextmanager
import duckdb
import pandas as pd


class DataProvider:
    """Class in charge of quering data from the DB"""

    @contextmanager
    def _connect(self):
        # To be used with `with`
        try:
            con = duckdb.connect(
                database="../orchestration/data/coches.net.duckdb",
                read_only=True,
                config={"access_mode": "READ_ONLY"},
            )
            yield con
        finally:
            con.close()

    def _get_vehicle_table(self, vehicle: str):
        return "stg_cars" if vehicle == "coches" else "stg_motorcycles"

    def _get_price__table(self, vehicle: str):
        return "fct_car_prices" if vehicle == "coches" else "fct_motorcycle_prices"

    def query_general_data_by_parameters(
        self,
        vehicle: str,
        title: str = None,
        km_min: int = None,
        km_max: int = None,
        price_min: int = None,
        price_max: int = None,
        fuel: list = None,
        offer: list = None,
        provinces: list = None,
    ) -> pd.DataFrame:
        table = self._get_vehicle_table(vehicle)
        query = f"""
            SELECT 
               {'motorcycle_id' if vehicle == "motos" else 'car_id'},
               title,
               km,
               year,
               main_province,
               fuel_type,
               price
            FROM analytics.{table}
            WHERE 
        """

        # Append conditions
        # Title
        if title is not None and title:
            for word in title.split(" "):
                query += f"title ILIKE '%{word}%' AND "
        # KM
        if km_min is not None:
            query += f"km >= {km_min} AND "
        if km_max is not None:
            query += f"km <= {km_max} AND "
        # Price
        if price_min is not None:
            query += f"price >= {price_min} AND "
        if price_max is not None:
            query += f"price <= {price_max} AND "
        # Fuel
        if fuel is not None and fuel:
            query += "("
            for elem in fuel:
                query += f"fuel_type = '{elem}' OR "
            query = query[:-4]
            query += ") "
            query += "AND "
        # Offer
        # Province
        if provinces is not None and provinces:
            query += "main_province IN ("
            for elem in provinces:
                query += f"'{elem}',"
            query += ") AND "

        # To ease the filters append each one includes and "AND " at the end
        # Remove the last one from the query before execute
        query = query[:-5]
        with self._connect() as con:
            df = con.cursor().execute(query).df()
        return df

    def query_fuel_types(self, vehicle: str):
        table = self._get_vehicle_table(vehicle)
        query = f"""
            SELECT 
                DISTINCT(fuel_type)
            FROM analytics.{table};
            """
        with self._connect() as con:
            elems = [col[0] for col in con.cursor().execute(query).fetchall()]
        return elems

    def query_offer_types(self, vehicle: str):
        table = self._get_vehicle_table(vehicle)
        query = f"""
            SELECT 
                DISTINCT(offer_type)
            FROM analytics.{table};
            """
        with self._connect() as con:
            elems = [col[0] for col in con.cursor().execute(query).fetchall()]
        return elems

    def query_provinces(self, vehicle: str):
        table = self._get_vehicle_table(vehicle)
        query = f"""
            SELECT 
                DISTINCT(main_province)
            FROM analytics.{table};
            """
        with self._connect() as con:
            elems = [col[0] for col in con.cursor().execute(query).fetchall()]
        return elems

    def query_vehicle_resorces(self, vehicle: str, id: str):
        table = self._get_vehicle_table(vehicle)
        query = f"""
            SELECT 
                resources
            FROM analytics.{table}
            WHERE motorcycle_id = {id};
            """
        elems = []
        with self._connect() as con:
            elems = [col[0] for col in con.cursor().execute(query).fetchall()]
        return elems

    def get_price_over_time(self, vehicle: str, vehicle_id: str):
        table = self._get_price__table(vehicle)
        query = f"""
            SELECT
                date_key,
                price
            FROM analytics.{table}
            WHERE motorcycle_id = {vehicle_id}
        """
        with self._connect() as con:
            df = con.cursor().execute(query).df()
        return df
