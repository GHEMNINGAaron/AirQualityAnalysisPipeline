import json
from confluent_kafka import Consumer, KafkaError
import time
from hdfs import InsecureClient

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

all_data = []

# Configuration HDFS
hdfs_client = InsecureClient('http://hadoop-namenode:9870', user='root')

try:
    # Boucle infinie de consommation Kafka
    while True:
        msg = consumer.poll(10.0)  # Attend jusqu'à 10 secondes un message

        if msg is None:
            print("Aucun message reçu... en attente.")
            continue  # Pas de message, on continue la boucle

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"Fin de partition : {msg.topic()} [{msg.partition()}]")
            else:
                print(f"Erreur Kafka : {msg.error()}")
        else:
            # Message reçu et valide
            data = msg.value().decode('utf-8')
            key = msg.key().decode('utf-8') if msg.key() else "no-key"

            print(f"📥 Message reçu : clé={key}, valeur={data}")

            # Ajoute le message à la liste
            all_data.append(json.loads(data))
            print(f"Total de messages reçus : {len(all_data)}")

        # ➡️ Exécuter un flush après avoir reçu un certain nombre de messages (par ex. 10)
        if len(all_data) >= 10:
            filename = 'air_quality_data.json'

            # Sauvegarde locale
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            print(f"✅ {len(all_data)} messages sauvegardés dans {filename}")

            # Upload sur HDFS
            try:
                hdfs_path = f'/data/air_quality/{filename}'
                
                # ➡️ Écriture directe de l'ensemble des données
                hdfs_client.write(
                    hdfs_path,
                    data=json.dumps(all_data, ensure_ascii=False, indent=4),
                    overwrite=True,
                    encoding='utf-8'
                )

                print(f"✅ Fichier {filename} uploadé sur HDFS à {hdfs_path} !")


            except Exception as e:
                print(f"❌ Erreur HDFS : {e}")

except KeyboardInterrupt:
    print("Arrêt du consumer (CTRL+C)")

    # Dernier flush si messages en attente
    if all_data:
        filename = 'air_quality_data_final.json'

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)

        try:
            hdfs_path = f'/data/air_quality/{filename}'

            hdfs_client.write(
                hdfs_path,
                data=json.dumps(all_data, ensure_ascii=False, indent=4),
                overwrite=True,
                encoding='utf-8'
            )

            print(f"✅ Derniers messages sauvegardés sur HDFS dans {hdfs_path}")

        except Exception as e:
            print(f"❌ Erreur finale HDFS : {e}")

finally:
    consumer.close()
