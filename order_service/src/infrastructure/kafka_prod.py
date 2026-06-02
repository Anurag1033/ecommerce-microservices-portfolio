import json
from confluent_kafka import Producer
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9094")

producer_config = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'order_service_producer'
}

# Initialize a singleton producer
producer = Producer(producer_config)

def delivery_report(err, msg):
    """Callback triggered by Kafka once a message is delivered (or fails)."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def publish_order_created_event(order_dict: dict):
    """Publishes the OrderCreated event to the 'orders' topic."""
    topic = 'orders'
    # The key ensures all events for the same order go to the same Kafka partition
    key = str(order_dict['id'])
    value = json.dumps(order_dict)

    producer.produce(
        topic=topic,
        key=key.encode('utf-8'),
        value=value.encode('utf-8'),
        callback=delivery_report
    )
    
    # Flush ensures the message is sent to the broker immediately
    producer.flush()