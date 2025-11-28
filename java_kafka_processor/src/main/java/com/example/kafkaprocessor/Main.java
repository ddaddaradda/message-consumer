package com.example.kafkaprocessor;

import com.example.kafkaprocessor.consumer.MessageConsumer;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class Main {
    public static void main(String[] args) {
        Properties props = loadProperties();
        MessageConsumer consumer = new MessageConsumer(props);

        // Add a shutdown hook to gracefully stop the consumer
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutdown hook triggered...");
            consumer.stop();
        }));

        consumer.run();
    }

    private static Properties loadProperties() {
        Properties props = new Properties();
        try (InputStream input = Main.class.getClassLoader().getResourceAsStream("application.properties")) {
            if (input == null) {
                System.out.println("Sorry, unable to find application.properties");
                System.exit(1);
            }
            props.load(input);
        } catch (IOException ex) {
            ex.printStackTrace();
            System.exit(1);
        }
        return props;
    }
}
