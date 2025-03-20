FROM python:3.9-slim

WORKDIR /app

COPY producer.py .

RUN pip install requests  confluent_kafka

CMD ["python", "producer.py"]
