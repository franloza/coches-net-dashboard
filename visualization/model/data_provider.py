import duckdb
import pandas as pd


class DataProvider:
    """Class in charge of quering data from the DB"""

    def __init__(self) -> None:
        self._con = duckdb.connect(
            database="../orchestration/data/coches.net.duckdb", read_only=True
        )

    def query_data_by_parameters(
        self,
        vehicle: str,
        title: str = None,
        km_min: int = None,
        km_max: int = None,
        fuel: list = None,
        offer: list = None,
    ) -> pd.DataFrame:
        query = f"""
            SELECT 
                id,
                creationDate::timestamp as creationDate, 
                title,
                'www.coches.net' || url as url, 
                km::int as km,
                year::int as year, 
                cubicCapacity,
                location_mainProvince as mainProvince, 
                fuelType,
                isFinanced::boolean as isFinanced,
                isCertified::boolean as isCertified,
                isProfessional,
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
        # Fuel
        if fuel is not None and fuel:
            query += "("
            for elem in fuel:
                query += f"fuelType = '{elem}' OR "
            query = query[:-4]
            query += ") "
            query += "AND "
        # Offer

        # To ease the filters append each one includes and "AND " at the end
        # Remove the last one from the query before execute
        query = query[:-5]
        return self._con.execute(query).df()
