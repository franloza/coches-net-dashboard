FROM python:3.8-slim

RUN python -m pip install --upgrade pip

# Checkout and install dagster libraries needed to run the gRPC server
RUN pip install \
    dagster-postgres==0.15.0 \
    dagster-docker==0.15.0

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add repository code
COPY orchestration /orchestration
COPY transformation /transformation
WORKDIR /orchestration/data_manager/

ENV PYTHONPATH "${PYTHONPATH}:/orchestration/data_manager/repository/"

# Run dagster gRPC server on port 4444
EXPOSE 4444

CMD bash -c "dagster api grpc -h 0.0.0.0 -p 4444 -f repository/repository.py -d /orchestration/data_manager/repository/"
