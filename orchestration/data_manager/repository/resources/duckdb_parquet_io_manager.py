import os

import duckdb
import pandas as pd

from dagster import Field, AssetMaterialization, AssetKey
from dagster import io_manager
from dagster.seven.temp_dir import get_system_temp_directory

from .parquet_io_manager import ParquetIOManager


class DuckDBParquetIOManager(ParquetIOManager):
    """Stores data in parquet files and creates duckdb views over those files."""

    def __init__(self, download_path: str, duckdb_path: str):
        super().__init__(download_path)
        if duckdb_path.startswith("./"):
            duckdb_path = os.path.join(os.getcwd(), duckdb_path[2:])
        self._duckdb_path = duckdb_path

    def handle_output(self, context, obj):
        if obj is not None:
            yield from super().handle_output(context, obj)
            con = self._connect_duckdb(context)

            to_scan = os.path.join(self._download_path, "*.parquet")
            table_name = context.name
            con.execute(
                f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM '{to_scan}';"
            )
            context.log_event(
                AssetMaterialization(
                    asset_key=AssetKey(table_name),
                    description=f"Created table {table_name} in DuckDB",
                    metadata={"number of rows": obj.shape[0]},
                )
            )

    def load_input(self, context) -> pd.DataFrame:
        con = self._connect_duckdb(context)
        table_name = context.upstream_output.name
        return con.execute(f"SELECT * FROM {table_name}").fetchdf()

    def _connect_duckdb(self, context):
        return duckdb.connect(database=self._duckdb_path, read_only=False)


@io_manager(config_schema={"download_path": str, "duckdb_path": str})
def duckdb_parquet_io_manager(init_context):
    return DuckDBParquetIOManager(
        download_path=init_context.resource_config["download_path"],
        duckdb_path=init_context.resource_config["duckdb_path"],
    )
