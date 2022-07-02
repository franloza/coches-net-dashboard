# Coches.net dataset ingestion with Dagster

# Deployment (containerized)
1. Run `docker-compose build`
2. Run `docker-compose up`

# Deployment (local dagit)
1. Open file `workspace.yaml`
2. Uncomment the `python_file` block
    - To supress errors you can comment the `grpc_server` block, but it is not necessarily.
3. Make sure the `executable_path` path is pointing to your python virtual environment.
4. Run `dagit`