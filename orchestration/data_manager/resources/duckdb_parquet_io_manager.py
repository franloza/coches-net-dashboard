import os

import duckdb
import pandas as pd

from dagster import Field, AssetMaterialization, AssetKey
from dagster import io_manager
from dagster.seven.temp_dir import get_system_temp_directory

from .parquet_io_manager import ParquetIOManager


class DuckDBParquetIOManager(ParquetIOManager):
    """Stores data in parquet files and creates duckdb views over those files."""

    def __init__(self, download_dir: str, duckdb_path: str):
        super().__init__(download_dir)
        self._duckdb_path = duckdb_path

    def handle_output(self, context, obj: dict):
        if obj is not None:
            yield from super().handle_output(context, obj)
            if "://" not in self._duckdb_path:
                os.makedirs(os.path.dirname(self._duckdb_path), exist_ok=True)

            con = self._connect_duckdb(context)

            df = obj["items"]

            to_scan = self._get_path(context)
            table_name = context.name
            con.execute(
                f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM '{to_scan}';"
            )
            context.log_event(
                AssetMaterialization(
                    asset_key=AssetKey(table_name),
                    description=f"Created table {table_name} in DuckDB",
                    metadata={"number of rows": df.shape[0]},
                )
            )

    def load_input(self, context) -> pd.DataFrame:
        con = self._connect_duckdb(context)
        table_name = context.upstream_output.name
        return con.execute(f"SELECT * FROM {table_name}").fetchdf()

    def _connect_duckdb(self, context):
        return duckdb.connect(database=self._duckdb_path, read_only=False)


@io_manager(config_schema={"download_dir": str, "duckdb_path": str})
def duckdb_parquet_io_manager(init_context):
    return DuckDBParquetIOManager(
        download_dir=init_context.resource_config["download_dir"],
        duckdb_path=init_context.resource_config["duckdb_path"],
    )
