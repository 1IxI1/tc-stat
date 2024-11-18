FROM python:3.13-slim

WORKDIR /

COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

COPY .env /

CMD ["python3", "-m", "app"]
