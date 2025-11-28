package com.example.kafkaprocessor.processor;

import com.example.kafkaprocessor.model.*;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

public class LteDataProcessor implements MessageProcessor {
    @Override
    public List<ProcessedData> process(IncomingPayload payload) {
        try {
            String[] titleParts = payload.getTitle().split("_");
            String sensorId = titleParts[0];
            String phoneNum = titleParts[1];

            GnssData gnssData = payload.getGnss();
            TravelData travelData = payload.getTravel();
            List<ProcessedData> processedDataList = new ArrayList<>();
            long timeInterval = 5000;

            for (Map<String, ImuValues> imuMap : payload.getImu()) {
                for (Map.Entry<String, ImuValues> entry : imuMap.entrySet()) {
                    long time = Long.parseLong(entry.getKey());
                    ImuValues imuValues = entry.getValue();
                    int k = imuValues.getAccel().size() / 3;

                    for (int i = 0; i < k; i++) {
                        int index = i * 3;
                        ProcessedData data = new ProcessedData.Builder()
                                .sensorId(sensorId)
                                .phoneNum(phoneNum)
                                .time(time + (long)(i * (timeInterval / (double)k)))
                                .accel(imuValues.getAccel().get(index), imuValues.getAccel().get(index + 1), imuValues.getAccel().get(index + 2))
                                .gyro(imuValues.getGyro().get(index), imuValues.getGyro().get(index + 1), imuValues.getGyro().get(index + 2))
                                .attitude(imuValues.getAttitude().get(index), imuValues.getAttitude().get(index + 1))
                                .location(gnssData.getPosition().get(0), gnssData.getPosition().get(1))
                                .gnss(gnssData.getVelocity(), gnssData.getAltitude(), gnssData.getBearing())
                                .travel(travelData.getTime(), travelData.getDistance())
                                .build();
                        processedDataList.add(data);
                    }
                }
            }
            return processedDataList;
        } catch (Exception e) {
            System.err.println("Error processing LTE data: " + e.getMessage());
            return Collections.emptyList();
        }
    }
}
