FROM python:3.9-slim
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./ /visualization/
WORKDIR /visualization
CMD gunicorn -b 0.0.0.0:80 app:server
