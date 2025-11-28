package com.example.kafkaprocessor.processor;

import com.example.kafkaprocessor.model.IncomingPayload;
import com.example.kafkaprocessor.model.ProcessedData;

import java.util.List;

/**
 * Interface for processing messages.
 */
public interface MessageProcessor {
    List<ProcessedData> process(IncomingPayload payload);
}
