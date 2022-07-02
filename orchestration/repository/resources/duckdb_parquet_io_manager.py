import os

import duckdb
import pandas as pd

from dagster import Field, AssetMaterialization, AssetKey
from dagster import io_manager
from dagster.seven.temp_dir import get_system_temp_directory

from .parquet_io_manager import ParquetIOManager


class DuckDBParquetIOManager(ParquetIOManager):
    """Stores data in parquet files and creates duckdb views over those files."""

    def handle_output(self, context, obj):
        if obj is not None:
            yield from super().handle_output(context, obj)
            con = self._connect_duckdb(context)

            path = self._get_path(context)
            to_scan = os.path.join(os.path.dirname(path), "*.parquet")
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
        return duckdb.connect(
            database=context.resource_config["duckdb_path"], read_only=False
        )


@io_manager(
    config_schema={"base_path": Field(str, is_required=False), "duckdb_path": str}
)
def duckdb_parquet_io_manager(init_context):
    return DuckDBParquetIOManager(
        base_path=init_context.resource_config.get(
            "base_path", get_system_temp_directory()
        )
    )
