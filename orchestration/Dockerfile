FROM python:3.8-slim

RUN pip install \
    dagster==0.15.0 \
    dagster-graphql==0.15.0 \
    dagit==0.15.0 \
    dagster-postgres==0.15.0 \
    dagster-docker==0.15.0

# Set $DAGSTER_HOME and copy dagster instance and workspace YAML there
ENV DAGSTER_HOME=/opt/dagster/dagster_home/

RUN mkdir -p $DAGSTER_HOME

COPY dagster.yaml workspace.yaml $DAGSTER_HOME

WORKDIR $DAGSTER_HOME
