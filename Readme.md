# BigData Pipeline Project

This project demonstrates a simple data pipeline using Kafka, Docker, and Python. The pipeline fetches air quality data from the OpenAQ API, sends it to a Kafka topic using a producer, and consumes the data from the topic using a consumer.

## Project Structure

```
BigData-pipeline/
│
├── consumer/
│   ├── consumer.py
│   └── Dockerfile
│
├── producer/
│   ├── producer.py
│   └── Dockerfile
│
├── docker-compose.yml
└── Readme.md
```

## Components

### Producer

The producer fetches air quality data from the OpenAQ API and sends it to a Kafka topic.

- **File:** `producer/producer.py`
- **Dockerfile:** `producer/Dockerfile`

### Consumer

The consumer reads data from the Kafka topic and processes it. In this example, it saves the data to a JSON file.

- **File:** `consumer/consumer.py`
- **Dockerfile:** `consumer/Dockerfile`

### Docker Compose

The `docker-compose.yml` file sets up the necessary services, including Kafka, Zookeeper, the producer, and the consumer.

## How to Run

1. **Clone the repository:**

  ```sh
  git clone <repository-url>
  cd BigData-pipeline
  ```

2. **Build and start the services:**

  ```sh
  docker-compose up --build
  ```

3. **Check the logs:**

  The producer will fetch data from the OpenAQ API and send it to the Kafka topic. The consumer will read the data from the topic and save it to JSON files.

## Configuration

- **Kafka Configuration:** The Kafka broker and Zookeeper are configured in the `docker-compose.yml` file.
- **API Key:** The OpenAQ API key is hardcoded in the `producer/producer.py` file. Replace it with your own API key if necessary.

## Dependencies

- Docker
- Docker Compose
- Python 3.9
- Confluent Kafka Python library
- Requests library (for the producer)
- HDFS library (for the consumer, if needed)

## License

This project is licensed under the MIT License.
