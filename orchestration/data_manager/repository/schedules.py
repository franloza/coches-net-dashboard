from dagster import schedule

from jobs import build_datasets_job


@schedule(
    cron_schedule="0 * * * *",
    job=build_datasets_job,
    execution_timezone="US/Central",
)
def build_cars_dataset_schedule(_context):
    """
    A schedule definition. This example schedule runs once each hour.

    For more hints on running jobs with schedules in Dagster, see our documentation overview on
    schedules:
    https://docs.dagster.io/overview/schedules-sensors/schedules
    """
    return {}
