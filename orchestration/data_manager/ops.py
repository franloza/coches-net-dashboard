from dagster import Out, Output, op, Int, Field
import pandas as pd


def download_items_op_factory(
    target_market: str,
    **kwargs,
):
    @op(
        name=f"download_{target_market}",
        out={target_market: Out(io_manager_key="warehouse_io_manager")},
        required_resource_keys={"coches_net_resource"},
        config_schema={
            "max_items": Field(
                Int,
                default_value=-1,
                is_required=False,
                description="Limits the number of items to download from the API. -1 means no limit",
            )
        },
        **kwargs
    )
    def download_items(context, **kwargs):
        """
        Downloads all of the items and creates a DataFrame with all the entries.
        """
        context.resources.coches_net_resource._target_market = target_market
        context.log.info("Downloading dataset from the API.")
        max_items = context.op_config["max_items"]
        if max_items == -1:
            max_items = None
        else:
            context.log.info(f"Limit of records set to {max_items}")
        result = pd.json_normalize(
            context.resources.coches_net_resource.search(limit=max_items), sep="_"
        )
        context.log.info(f"All records downloaded: {result.shape[0]} records")
        return Output(
            {
                "items": result
            },
            target_market,
        )

    return download_items
