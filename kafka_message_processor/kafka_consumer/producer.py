"""
Kafka Producer
"""
import json
from kafka import KafkaProducer
from config.settings import KAFKA_BROKERS, DESTINATION_TOPIC

def get_producer():
    """Returns a KafkaProducer instance."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def send_message(producer, message):
    """Sends a message to the destination topic."""
    producer.send(DESTINATION_TOPIC, message)
    producer.flush()
