FROM python:3.9-slim

WORKDIR /app

COPY consumer.py .

RUN pip install confluent-kafka hdfs

CMD ["python", "consumer.py"]
