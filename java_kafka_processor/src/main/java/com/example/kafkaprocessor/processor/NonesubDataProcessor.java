package com.example.kafkaprocessor.processor;

import com.example.kafkaprocessor.model.GnssData;
import com.example.kafkaprocessor.model.IncomingPayload;
import com.example.kafkaprocessor.model.ProcessedData;

import java.util.Collections;
import java.util.List;

public class NonesubDataProcessor implements MessageProcessor {
    @Override
    public List<ProcessedData> process(IncomingPayload payload) {
        try {
            String[] titleParts = payload.getTitle().split("_");
            String phoneNum = titleParts[0];

            GnssData gnssData = payload.getGnss();

            ProcessedData data = new ProcessedData.Builder()
                    .phoneNum(phoneNum)
                    .time(payload.getTime())
                    .location(gnssData.getPosition().get(0), gnssData.getPosition().get(1))
                    .gnss(gnssData.getVelocity(), gnssData.getAltitude(), gnssData.getBearing())
                    .build();

            return Collections.singletonList(data);
        } catch (Exception e) {
            System.err.println("Error processing Nonesub data: " + e.getMessage());
            return Collections.emptyList();
        }
    }
}
