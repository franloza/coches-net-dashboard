import os
from dagster import job, file_relative_path
from dagster_dbt import dbt_cli_resource, dbt_snapshot_op, dbt_build_op

from ops import download_items_op_factory
from resources.coches_net import coches_net_resource
from resources.duckdb_parquet_io_manager import duckdb_parquet_io_manager


DATABASE_FILE_NAME = 'coches.net.duckdb'
TRANSFORMATION_DIR = os.path.abspath(file_relative_path(__file__, '../../../transformation'))
DOCKER_CONFIG = {
    "resources": {
        "warehouse_io_manager": {
            "config": {
                "download_dir": "/tmp/",
                "duckdb_path": f"/tmp/{DATABASE_FILE_NAME}",
            }
        }
    }
}
LOCAL_CONFIG = {
    "resources": {
        "warehouse_io_manager": {
            "config": {
                "download_dir": "/tmp/",
                "duckdb_path": os.path.abspath(file_relative_path(__file__, f"../../data/{DATABASE_FILE_NAME}"))
            }
        }
    }
}


@job(
    resource_defs={
        "warehouse_io_manager": duckdb_parquet_io_manager,
        "coches_net_resource": coches_net_resource,
        "dbt":  dbt_cli_resource.configured({
            "project_dir": TRANSFORMATION_DIR,
            "profiles_dir": TRANSFORMATION_DIR
        })
    }
)
def build_datasets_job():
    """
    Downloads all cars and motorbikes from the Coches.net API.
    """
    # Extract and load data
    cars = download_items_op_factory(target_market="coches")()
    motorbikes = download_items_op_factory(target_market="motos")()
    # Transform data
    dbt_build_op(start_after=dbt_snapshot_op([cars, motorbikes]))


if __name__ == "__main__":
    dev_config = dict(LOCAL_CONFIG)
    # Uncomment to limit the number of records
    # max_items = 1000
    # dev_config['ops'] = {
    #    'download_coches': {'config': {'max_items': max_items}},
    #    'download_motos': {'config': {'max_items': max_items}}
    # }
    build_datasets_job.execute_in_process(run_config=dev_config)
