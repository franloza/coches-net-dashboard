import os
from datetime import datetime

import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa

from dagster import (
    AssetKey,
    IOManager,
    MetadataEntry,
    OutputContext,
)


class ParquetIOManager(IOManager):
    """
    This IOManager will take in a pandas dataframe and store it in parquet at the
    specified path.

    It stores outputs for different partitions in different filepaths.

    Downstream ops can load this dataframe
    """

    def __init__(self, download_dir: str):
        self._download_dir = os.path.dirname(download_dir)

    def handle_output(self, context: OutputContext, obj: dict):
        if "://" not in self._download_dir:
            os.makedirs(self._download_dir, exist_ok=True)

        df = obj["items"]
        row_count = len(df)
        path = self._get_path(context)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, where=self._get_path(context))
        context.log.info(f"Parquet file written {path}")
        yield MetadataEntry.int(value=row_count, label="row_count")
        yield MetadataEntry.path(path=path, label="path")

    def load_input(self, context) -> pd.DataFrame:
        path = self._get_path(context.upstream_output)
        return pd.read_parquet(path)

    def _get_path(self, context: OutputContext):
        return os.path.join(self._download_dir, f"{context.name}.parquet")

    def get_output_asset_key(self, context: OutputContext):
        return AssetKey([*self._download_dir.split("://"), context.name])
