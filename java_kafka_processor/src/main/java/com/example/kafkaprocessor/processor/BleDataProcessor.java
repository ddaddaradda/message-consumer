package com.example.kafkaprocessor.processor;

import com.example.kafkaprocessor.model.GnssData;
import com.example.kafkaprocessor.model.ImuValues;
import com.example.kafkaprocessor.model.IncomingPayload;
import com.example.kafkaprocessor.model.ProcessedData;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

public class BleDataProcessor implements MessageProcessor {
    @Override
    public List<ProcessedData> process(IncomingPayload payload) {
        try {
            String[] titleParts = payload.getTitle().split("_");
            String sensorId = titleParts[0];
            String phoneNum = titleParts[1];

            GnssData gnssData = payload.getGnss();
            List<ProcessedData> processedDataList = new ArrayList<>();

            for (Map<String, ImuValues> imuMap : payload.getImu()) {
                for (Map.Entry<String, ImuValues> entry : imuMap.entrySet()) {
                    long time = Long.parseLong(entry.getKey());
                    ImuValues imuValues = entry.getValue();

                    ProcessedData data = new ProcessedData.Builder()
                            .sensorId(sensorId)
                            .phoneNum(phoneNum)
                            .time(time)
                            .accel(imuValues.getAccel().get(0), imuValues.getAccel().get(1), imuValues.getAccel().get(2))
                            .gyro(imuValues.getGyro().get(0), imuValues.getGyro().get(1), imuValues.getGyro().get(2))
                            .attitude(imuValues.getAttitude().get(0), imuValues.getAttitude().get(1))
                            .location(gnssData.getPosition().get(0), gnssData.getPosition().get(1))
                            .gnss(gnssData.getVelocity(), gnssData.getAltitude(), gnssData.getBearing())
                            .build();
                    processedDataList.add(data);
                }
            }
            return processedDataList;
        } catch (Exception e) {
            // In a real app, use a logger
            System.err.println("Error processing BLE data: " + e.getMessage());
            return Collections.emptyList();
        }
    }
}
