from dagster import schedule

from orchestration.jobs import build_cars_dataset


@schedule(cron_schedule="0 * * * *", job=build_cars_dataset, execution_timezone="US/Central")
def build_cars_dataset_schedule(_context):
    """
    A schedule definition. This example schedule runs once each hour.

    For more hints on running jobs with schedules in Dagster, see our documentation overview on
    schedules:
    https://docs.dagster.io/overview/schedules-sensors/schedules
    """
    run_config = {}
    return run_config
