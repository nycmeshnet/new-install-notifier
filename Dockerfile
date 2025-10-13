FROM python:3.12-slim-bookworm

WORKDIR /usr/src/app

COPY app.py ./
COPY channels.json ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT python3 app.py
