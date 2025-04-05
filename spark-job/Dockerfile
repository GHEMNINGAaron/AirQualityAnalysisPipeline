FROM bitnami/spark:latest

WORKDIR /app

COPY analyse.py .

RUN pip install pyspark pandas matplotlib

CMD ["python", "analyse.py"]