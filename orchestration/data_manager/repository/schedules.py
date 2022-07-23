from dagster import schedule

from jobs import build_datasets_job, PROD_CONFIG


@schedule(
    cron_schedule="0 0 * * *",
    job=build_datasets_job,
    execution_timezone="UTC",
)
def build_cars_dataset_schedule(context):
    return PROD_CONFIG
