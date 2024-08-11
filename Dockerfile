FROM python:3.10.12-slim-bookworm

ENV TZ="Europe/Brussels"

WORKDIR /eventHandler

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . /eventHandler/

CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "eventHandler.app:app"]
