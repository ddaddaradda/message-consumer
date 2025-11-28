package com.example.kafkaprocessor.producer;

import com.example.kafkaprocessor.model.ProcessedData;
import com.google.gson.Gson;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

import java.util.Properties;

public class MessageProducer implements AutoCloseable {
    private final KafkaProducer<String, String> producer;
    private final Gson gson = new Gson();

    public MessageProducer(Properties props) {
        Properties producerProps = new Properties();
        producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, props.getProperty("kafka.brokers"));
        producerProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        producerProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        
        this.producer = new KafkaProducer<>(producerProps);
    }

    public void send(String destinationTopic, ProcessedData data) {
        String json = gson.toJson(data);
        producer.send(new ProducerRecord<>(destinationTopic, json));
    }

    public void flush() {
        producer.flush();
    }

    @Override
    public void close() {
        producer.close();
    }
}