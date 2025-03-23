FROM python:3.9-slim

WORKDIR /app

COPY consumer.py .

RUN pip install confluent-kafka hdfs datetime

CMD ["python", "consumer.py"]
