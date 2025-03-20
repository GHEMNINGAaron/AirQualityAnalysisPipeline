import requests
import json
from confluent_kafka import Producer

# Configuration du producteur Kafka
conf = {'bootstrap.servers': 'kafka:9092'}  # Remplace par l'adresse de ton serveur Kafka si nécessaire
producer = Producer(conf)

# Fonction de callback pour vérifier si le message est bien envoyé
def delivery_report(err, msg):
    if err is not None:
        print(f"Échec de l'envoi : {err}")
    else:
        print(f"Message envoyé : {msg.value()} à {msg.topic()} [{msg.partition()}]")

# Fonction pour récupérer les données de l'API OpenAQ (mesures)
def fetch_air_quality_data():
    url = "https://api.openaq.org/v3/sensors/3917/measurements" 
    headers = {"X-API-Key": "2ef284aac25b9937ae7949ba18212470bc8e0160824873124aa1921c5086762e"} 

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('results', [])  # Retourne les résultats si la requête réussit
        elif response.status_code == 401:
            print("Erreur 401 : Clé API invalide ou expirée.")
            return None
        else:
            print(f"Erreur {response.status_code} : {response.text}")
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        return None

# Envoi des données à Kafka
def send_to_kafka(topic, data):
    for record in data:
        try:
            # Envoie chaque enregistrement dans le topic Kafka
            producer.produce(topic, key=str(record.get("location", "unknown")), value=json.dumps(record), callback=delivery_report)
        except Exception as e:
            print(f"Erreur lors de l'envoi à Kafka : {e}")
    producer.flush()  # Assure que tous les messages sont envoyés

# Exécution principale

topic = "air_quality"  # Nom du topic Kafka où envoyer les données
data = fetch_air_quality_data()  # Récupère les données depuis l'API OpenAQ
if data:
    send_to_kafka(topic, data)  # Envoie les données à Kafka si elles sont récupérées
else:
    print("Aucune donnée récupérée.")  # Affiche un message si aucune donnée n'est récupérée