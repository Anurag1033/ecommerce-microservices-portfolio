import json
from confluent_kafka import Consumer, KafkaError
from src.config import Config
from src.use_cases.inventory_ops import process_order_created_event

def start_consumer():
    consumer_config = {
        'bootstrap.servers': Config.KAFKA_BROKER,
        'group.id': 'inventory_service_group',
        'auto.offset.reset': 'earliest', # Read from the beginning if it's a new consumer group
        'enable.auto.commit': False      # We will manually commit offsets only after successful processing
    }
    
    consumer = Consumer(consumer_config)
    consumer.subscribe(['orders'])
    
    print("🎧 Inventory Service Consumer started. Listening to 'orders' topic...")
    
    try:
        while True:
            # Poll for messages every 1.0 second
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Kafka error: {msg.error()}")
                    break
            
            # Message received
            event_payload = json.loads(msg.value().decode('utf-8'))
            print(f"📥 Received event: {event_payload.get('event_type')} for Order {event_payload.get('id')}")
            
            if event_payload.get('event_type') == 'OrderCreated':
                # Process the business logic
                process_order_created_event(event_payload)
                
                # Idempotency / Reliability: Only commit the offset AFTER successful processing
                consumer.commit(asynchronous=False)
                
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()