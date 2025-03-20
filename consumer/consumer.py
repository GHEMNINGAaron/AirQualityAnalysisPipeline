import json
from confluent_kafka import Consumer, KafkaError
import time

# Configuration du consumer Kafka
conf = {
    'bootstrap.servers': 'kafka:9092',      # Adresse du broker Kafka (Docker ou autre)
    'group.id': 'air_quality_consumer_group', # ID du groupe de consommateurs
    'auto.offset.reset': 'earliest'         # Reprendre depuis le début si pas d'offset stocké
}

# Initialisation du consumer
consumer = Consumer(conf)

# Topic à consommer
topic = 'air_quality'
consumer.subscribe([topic])

print(f"En écoute sur le topic '{topic}'...")

try:
    while True:
        msg = consumer.poll(1.0)  # Attend 1 seconde un message

        if msg is None:
            continue  # Pas de message reçu, boucle continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # Fin de la partition, pas d'erreur bloquante
                print(f"Fin de partition : {msg.topic()} [{msg.partition()}]")
            else:
                # Erreur sérieuse
                print(f"Erreur Kafka : {msg.error()}")
        else:
            # Message reçu et valide
            data = msg.value().decode('utf-8')
            key = msg.key().decode('utf-8') if msg.key() else "no-key"

            print(f"Message reçu : clé={key}, valeur={data}")

            # ➡️ Ici tu peux envoyer vers HDFS, fichier, ou base de données
            # Exemple simple : Écriture dans un fichier JSON (un fichier par message)
            timestamp = int(time.time())
            filename = f'air_quality_{timestamp}.json'
            with open(filename, 'a', encoding='utf-8') as f:
                json.dump(json.loads(data), f, ensure_ascii=False, indent=4)
                f.write('\n')
            print(f"Message sauvegardé dans {filename}")

except KeyboardInterrupt:
    print("Arrêt du consumer (CTRL+C)")

finally:
    # Clean up
    consumer.close()
