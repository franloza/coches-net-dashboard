from dagster import job

from ops import download_items_op_factory
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
    }
}


@job(
    resource_defs={
        "warehouse_io_manager": duckdb_parquet_io_manager,
        "coches_net_resource": coches_net_resource
    }
)
def build_datasets_job():
    """
    Downloads all cars and motorbikes from the Coches.net API.
    """
    cars = download_items_op_factory(target_market="coches")()
    motorbikes = download_items_op_factory(target_market="motos")()


if __name__ == "__main__":
    build_datasets_job.execute_in_process(run_config=local_config)
