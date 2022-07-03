from dagster import job

from ops import download_items
from resources.coches_net import coches_net_resource
from resources.duckdb_parquet_io_manager import duckdb_parquet_io_manager

my_coches_resource = coches_net_resource.configured({})


@job(
    resource_defs={
        "coches_net_resource": my_coches_resource,
        "warehouse_io_manager": duckdb_parquet_io_manager.configured(
            {"duckdb_path": "/tmp/coches.net.duckdb"},
        ),
    }
)
def build_cars_dataset():
    """
    Downloads all items from the Coches.net API.
    """
    items = download_items()
