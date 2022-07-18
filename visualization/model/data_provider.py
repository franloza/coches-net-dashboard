import duckdb
import pandas as pd


class DataProvider:
    """Class in charge of quering data from the DB"""

    def __init__(self) -> None:
        try:
            self.connect()
        except RuntimeError:
            self._con = None

    @property
    def connection(self):
        if self._con is None:
            self.connect()
        return self._con

    def connect(self):
        self._con = duckdb.connect(
            database="../orchestration/data/coches.net.duckdb",
            read_only=True,
            config={"access_mode": "READ_ONLY"},
        )

    def query_data_by_parameters(
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
        query = f"""
            SELECT 
                id,
                title,
                km::int as km,
                year::int as year, 
                cubicCapacity,
                location_mainProvince as mainProvince, 
                fuelType,
                publishedDate::timestamp as publishedDate,
                price_amount as price,
                FROM {vehicle} 
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
                query += f"fuelType = '{elem}' OR "
            query = query[:-4]
            query += ") "
            query += "AND "
        # Offer
        # Province
        if provinces is not None and provinces:
            query += "mainProvince IN ("
            for elem in provinces:
                query += f"'{elem}',"
            query += ") AND "

        # To ease the filters append each one includes and "AND " at the end
        # Remove the last one from the query before execute
        query = query[:-5]
        return self._con.cursor().execute(query).df()

    def query_fuel_types(self, vehicle: str):
        query = f"""
            SELECT 
                DISTINCT(fuelType)
                FROM {vehicle};
            """
        return [col[0] for col in self.connection.cursor().execute(query).fetchall()]

    def query_offer_types(self, vehicle: str):
        query = f"""
            SELECT 
                DISTINCT(offerType_literal)
                FROM {vehicle};
            """
        return [col[0] for col in self.connection.cursor().execute(query).fetchall()]

    def query_provinces(self, vehicle: str):
        query = f"""
            SELECT 
                DISTINCT(mainProvince)
                FROM {vehicle};
            """
        return [col[0] for col in self.connection.cursor().execute(query).fetchall()]

    def query_vehicle_resorces(self, vehicle: str, id: str):
        query = f"""
            SELECT 
                resources
                FROM {vehicle}
                WHERE id = {id};
            """
        return [col[0] for col in self.connection.cursor().execute(query).fetchall()]
