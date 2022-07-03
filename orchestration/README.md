# Coches.net dataset ingestion with Dagster

## Deployment (containerized)
1. Run `docker-compose build`
2. Run `docker-compose up`

**Warning** By default the job will persist all data inside the `/tmp` folder of the container. There is a volumne
set up to map a folder `data` to `/tmp`. The folder `data` must be at the same level as the `docker-compose` file.

## Deployment (local dagit)
1. Open file `workspace.yaml`
2. Uncomment the `python_file` block
    - To supress errors you can comment the `grpc_server` block, but it is not necessarily.
3. Make sure the `executable_path` path is pointing to your python virtual environment.
4. Run `dagit`