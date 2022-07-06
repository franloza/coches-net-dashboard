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

    def __init__(self, download_path: str):
        if download_path.startswith("./"):
            download_path = os.path.join(os.getcwd(), download_path[2:])
        self._download_path = download_path

    def handle_output(self, context: OutputContext, obj: dict):
        path = self._get_path(context)
        if "://" not in self._download_path:
            os.makedirs(os.path.dirname(path), exist_ok=True)

        market = obj["target_market"]
        df = obj["items"]

        row_count = len(df)
        table = pa.Table.from_pandas(df)
        pq.write_to_dataset(
            table,
            root_path=path,
            partition_filename_cb=lambda x: f"{datetime.utcnow().strftime('%Y_%m_%d')}_{market}_{x}.parquet",
        )  # It appends by default
        context.log.info(f"Parquet file written {path}")
        yield MetadataEntry.int(value=row_count, label="row_count")
        yield MetadataEntry.path(path=path, label="path")

    def load_input(self, context) -> pd.DataFrame:
        path = self._get_path(context.upstream_output)
        return pd.read_parquet(path)

    def _get_path(self, context: OutputContext):
        return self._download_path

    def get_output_asset_key(self, context: OutputContext):
        return AssetKey([*self._download_path.split("://"), context.name])
