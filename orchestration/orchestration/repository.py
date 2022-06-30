from dagster import repository

from orchestration.jobs import build_cars_dataset
from orchestration.schedules import build_cars_dataset_schedule


@repository
def orchestration():
    """
    The repository definition for this orchestration Dagster repository.

    For hints on building your Dagster repository, see our documentation overview on Repositories:
    https://docs.dagster.io/overview/repositories-workspaces/repositories
    """
    jobs = [build_cars_dataset]
    schedules = [build_cars_dataset_schedule]

    return jobs + schedules
