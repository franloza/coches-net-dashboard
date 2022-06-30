from typing import List

from dagster import Out, Output, op, Int, Field
import pandas

@op(
    out={
        "items": Out(
            io_manager_key="warehouse_io_manager"
        )
    },
    required_resource_keys={"coches_net_resource"},
    config_schema={
        "max_items": Field(Int, default_value=-1, is_required=False,
                           description="Limits the number of items to download from the API. -1 means no limit")
    }
)
def download_items(context) -> Output[pandas.DataFrame]:
    """
    Downloads all of the items and creates a DataFrame with all the entries.
    """
    context.log.info(f"Downloading dataset from the API.")
    max_items = context.op_config["max_items"]
    if max_items == -1:
        max_items = None
    else:
        context.log.info(f"Limit of records set to {max_items}")
    result = pandas.json_normalize(context.resources.coches_net_resource.search(limit=max_items), sep='_')
    context.log.info(f"All records downloaded: {result.shape[0]} records")
    return Output(result, "items")

