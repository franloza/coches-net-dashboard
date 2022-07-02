import os
from typing import Union

import pandas
import pandas as pd

from dagster import AssetKey, IOManager, MetadataEntry, OutputContext, AssetMaterialization


class ParquetIOManager(IOManager):
    """
    This IOManager will take in a pandas dataframe and store it in parquet at the
    specified path.

    It stores outputs for different partitions in different filepaths.

    Downstream ops can load this dataframe
    """

    def __init__(self, base_path):
        self._base_path = base_path

    def handle_output(
        self, context: OutputContext, obj: pandas.DataFrame
    ):
        path = self._get_path(context)
        if "://" not in self._base_path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        row_count = len(obj)
        obj.to_parquet(path=path, index=False)
        context.log.info(f"Parquet file written {path}")
        yield MetadataEntry.int(value=row_count, label="row_count")
        yield MetadataEntry.path(path=path, label="path")

    def load_input(self, context) -> pandas.DataFrame:
        path = self._get_path(context.upstream_output)
        return pd.read_parquet(path)

    def _get_path(self, context: OutputContext):
        return os.path.join(self._base_path, f"{context.name}.parquet")

    def get_output_asset_key(self, context: OutputContext):
        return AssetKey([*self._base_path.split("://"), context.name])
