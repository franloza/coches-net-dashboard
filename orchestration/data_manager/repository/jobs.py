from dagster import job

from ops import download_items_op_factory
from resources.coches_net import coches_net_resource
from resources.duckdb_parquet_io_manager import duckdb_parquet_io_manager


DOCKER_CONFIG = {
    "resources": {
        "warehouse_io_manager": {
            "config": {
                "download_dir": "/tmp/",
                "duckdb_path": "/tmp/coches.net.duckdb",
            }
        }
    }
}
LOCAL_CONFIG = {
    "resources": {
        "warehouse_io_manager": {
            "config": {
                "download_dir": "/tmp/",
                "duckdb_path": "../../data/coches.net.duckdb",
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
    dev_config = dict(LOCAL_CONFIG)
    # Uncomment to limit the number of records
    # max_items = 1000
    # dev_config['ops'] = {
    #    'download_coches': {'config': {'max_items': max_items}},
    #    'download_motos': {'config': {'max_items': max_items}}
    # }
    build_datasets_job.execute_in_process(run_config=dev_config)
