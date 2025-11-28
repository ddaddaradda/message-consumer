"""
Kafka Consumer
"""
import json
import signal
import sys
import logging
from kafka import KafkaConsumer
from config.settings import KAFKA_BROKERS, SOURCE_TOPIC, CONSUMER_GROUP_ID, DESTINATION_TOPIC
from .producer import get_producer, send_message
from .processor import dispatch_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    global running
    logger.info("Shutdown signal received. Closing consumer...")
    running = False

def run_consumer():
    """Runs the Kafka consumer with graceful shutdown support."""
    global running

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    consumer = KafkaConsumer(
        SOURCE_TOPIC,
        bootstrap_servers=KAFKA_BROKERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=CONSUMER_GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    producer = get_producer()

    logger.info(f"Subscribed to topic: {SOURCE_TOPIC}")

    try:
        while running:
            # Poll with timeout to allow checking the running flag
            messages = consumer.poll(timeout_ms=1000)

            for topic_partition, records in messages.items():
                for message in records:
                    payload = message.value
                    logger.debug(f"Received message: {payload}")

                    # Dispatch the payload to the correct processor
                    processed_data = dispatch_processor(payload)

                    if processed_data:
                        # Send the processed data to the destination topic
                        for data_item in processed_data:
                            send_message(producer, data_item)
                        logger.info(f"Sent {len(processed_data)} processed messages to {DESTINATION_TOPIC}")
    except Exception as e:
        logger.error(f"Error in consumer loop: {e}", exc_info=True)
    finally:
        # Close resources gracefully
        logger.info("Closing consumer and producer...")
        consumer.close()
        producer.close()
        logger.info("Consumer shutdown complete")