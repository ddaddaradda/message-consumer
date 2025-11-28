package com.example.kafkaprocessor.consumer;

import com.example.kafkaprocessor.model.ProcessedData;
import com.example.kafkaprocessor.processor.ProcessorDispatcher;
import com.example.kafkaprocessor.producer.MessageProducer;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;

import java.time.Duration;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import java.util.stream.Collectors;

public class MessageConsumer {
    private final KafkaConsumer<String, String> consumer;
    private final MessageProducer producer;
    private final ProcessorDispatcher dispatcher;
    private final Properties props;
    private volatile boolean running = true;

    public MessageConsumer(Properties props) {
        this.props = props;
        this.producer = new MessageProducer(props);
        this.dispatcher = new ProcessorDispatcher();

        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, props.getProperty("kafka.brokers"));
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, props.getProperty("kafka.group.id"));
        consumerProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        this.consumer = new KafkaConsumer<>(consumerProps);
        List<String> sourceTopics = Arrays.asList(props.getProperty("kafka.source.topics").split(","));
        this.consumer.subscribe(sourceTopics);
    }

    public void run() {
        System.out.println("Consumer started. Subscribed to topics: " + consumer.subscription());
        try {
            while (running) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
                for (ConsumerRecord<String, String> record : records) {
                    String sourceTopic = record.topic();
                    System.out.println("Received message from topic " + sourceTopic + ": " + record.value());

                    List<ProcessedData> processedDataList = dispatcher.dispatch(sourceTopic, record.value());

                    if (processedDataList != null && !processedDataList.isEmpty()) {
                        String destinationTopic = props.getProperty("topic.mapping." + sourceTopic);
                        if (destinationTopic == null) {
                            System.err.println("No destination topic mapping found for source: " + sourceTopic);
                            continue;
                        }
                        
                        processedDataList.forEach(data -> producer.send(destinationTopic, data));
                        producer.flush();
                        System.out.println("Sent " + processedDataList.size() + " processed messages to " + destinationTopic);
                    }
                }
            }
        } finally {
            close();
        }
    }

    public void stop() {
        running = false;
    }

    private void close() {
        consumer.close();
        producer.close();
        System.out.println("Consumer and producer closed.");
    }
}