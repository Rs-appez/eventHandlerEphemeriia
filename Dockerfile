FROM python:3.13.5-slim-bookworm

ENV TZ="Europe/Brussels"

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . /app/

WORKDIR /app/eventHandler

CMD ["python", "main.py"]
