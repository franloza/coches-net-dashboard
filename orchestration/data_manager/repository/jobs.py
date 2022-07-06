from dagster import job

from ops import download_items
from resources.coches_net import coches_net_resource
from resources.duckdb_parquet_io_manager import duckdb_parquet_io_manager


docker_config = {
    "resources": {
        "warehouse_io_manager": {
            "config": {
                "download_path": "/tmp/items.parquet",
                "duckdb_path": "/tmp/coches.net.duckdb",
            }
        }
    }
}
local_config = {
    "resources": {
        "warehouse_io_manager": {
            "config": {
                "download_path": "./orchestration/data/items.parquet",  # relative from workspace path
                "duckdb_path": "./orchestration/data/coches.net.duckdb",
            }
        },
        "coches_net_resource": {"config": {"target_market": "motos"}},
    }
}


@job(
    resource_defs={
        "coches_net_resource": coches_net_resource,
        "warehouse_io_manager": duckdb_parquet_io_manager,
    }
)
def build_cars_dataset_job():
    """
    Downloads all items from the Coches.net API.
    """
    items = download_items()


if __name__ == "__main__":
    build_cars_dataset_job.execute_in_process(run_config=local_config)
