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
def fetch_air_quality_data(id):
    url = f'https://api.openaq.org/v3/sensors/{id}/measurements?limit=5' 
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
    i=1
    for record in data:
        try:
            # Envoie chaque enregistrement dans le topic Kafka
            producer.produce(topic, key=f"sensor_3917_data_{i}", value=json.dumps(record), callback=delivery_report)
            i+=1
        except Exception as e:
            print(f"Erreur lors de l'envoi à Kafka : {e}")
    producer.flush()  # Assure que tous les messages sont envoyés

# Exécution principale
SENSOR_ID = [5561, 15370, 5566, 5567, 5569, 5568, 5572, 5574, 5573, 4275113, 5578, 5579, 5656, 5580, 5581, 5582, 4275139, 5609, 5622, 5583, 5614]

topic = "air_quality"  # Nom du topic Kafka où envoyer les données
for id in SENSOR_ID:
    data = fetch_air_quality_data(id)  # Récupère les données depuis l'API OpenAQ
    if data:
        send_to_kafka(topic, data)  # Envoie les données à Kafka si elles sont récupérées
    else:
        print("Aucune donnée récupérée.")  # Affiche un message si aucune donnée n'est récupérée