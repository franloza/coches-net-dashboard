from dagster import repository

from jobs import build_datasets_job
from schedules import build_cars_dataset_schedule


@repository
def orchestration():
    """
    The repository definition for this orchestration Dagster repository.

    For hints on building your Dagster repository, see our documentation overview on Repositories:
    https://docs.dagster.io/overview/repositories-workspaces/repositories
    """
    jobs = [build_datasets_job]
    schedules = [build_cars_dataset_schedule]

    return jobs + schedules
