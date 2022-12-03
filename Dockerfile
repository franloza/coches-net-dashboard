FROM python:3.8

RUN python -m pip install --upgrade pip

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN pip install \
    dagster-graphql==0.15.0 \
    dagster-postgres==0.15.0 \
    dagster-docker==0.15.0

EXPOSE 4444

ENV DAGSTER_HOME=/opt/dagster/dagster_home/

RUN mkdir -p $DAGSTER_HOME

COPY orchestration/dagster.yaml $DAGSTER_HOME

WORKDIR /app

COPY orchestration orchestration
COPY transformation transformation
COPY orchestration/workspace-docker.yaml /app/workspace.yaml

RUN pip install --editable orchestration





