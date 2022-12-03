FROM python:3.8

RUN python -m pip install --upgrade pip

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /app/visualization

WORKDIR /app/visualization

CMD gunicorn -b 0.0.0.0:80 app:server
