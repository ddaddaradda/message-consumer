package com.example.kafkaprocessor.processor;

import com.example.kafkaprocessor.model.IncomingPayload;
import com.example.kafkaprocessor.model.ProcessedData;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.util.Collections;
import java.util.List;

public class ProcessorDispatcher {
    private final MessageProcessor bleProcessor = new BleDataProcessor();
    private final MessageProcessor lteProcessor = new LteDataProcessor();
    private final MessageProcessor lteV2Processor = new LteV2DataProcessor();
    private final MessageProcessor nonesubProcessor = new NonesubDataProcessor();
    private final Gson gson = new Gson();

    public List<ProcessedData> dispatch(String sourceTopic, String messageValue) {
        try {
            IncomingPayload payload = gson.fromJson(messageValue, IncomingPayload.class);

            // Dispatch based on the source topic name
            if (sourceTopic.contains("ble")) {
                return bleProcessor.process(payload);
            } else if (sourceTopic.contains("ltev2")) {
                return lteV2Processor.process(payload);
            } else if (sourceTopic.contains("ltev1")) {
                return lteProcessor.process(payload);
            } else if (sourceTopic.contains("nonesub")) {
                return nonesubProcessor.process(payload);
            } else {
                System.err.println("No processor found for topic: " + sourceTopic);
                return Collections.emptyList();
            }
        } catch (Exception e) {
            System.err.println("Error dispatching processor for topic " + sourceTopic + ": " + e.getMessage());
            return Collections.emptyList();
        }
    }
}
