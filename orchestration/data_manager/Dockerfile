#FROM python:3.8-slim
FROM python:3.8-slim

RUN python -m pip install --upgrade pip

# Checkout and install dagster libraries needed to run the gRPC server
RUN pip install \
    dagster==0.15.0 \
    dagster-postgres==0.15.0 \
    dagster-docker==0.15.0

# Prepare repository path
RUN mkdir orchestration/
RUN mkdir data_manager/
WORKDIR /orchestration/data_manager

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/orchestration/data_manager/repository/"

COPY . .

# Run dagster gRPC server on port 4444
EXPOSE 4444

CMD bash -c "dagster api grpc -h 0.0.0.0 -p 4444 -f repository/repository.py -d /orchestration/data_manager/repository/"
