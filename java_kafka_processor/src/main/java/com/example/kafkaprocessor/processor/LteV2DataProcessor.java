package com.example.kafkaprocessor.processor;

import com.example.kafkaprocessor.model.*;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

public class LteV2DataProcessor implements MessageProcessor {
    @Override
    public List<ProcessedData> process(IncomingPayload payload) {
        try {
            String[] titleParts = payload.getTitle().split("_");
            String sensorId = titleParts[0];
            String phoneNum = titleParts[1];

            GnssData gnssData = payload.getGnss();
            TravelData travelData = payload.getTravel();
            List<Double> locationList = payload.getLocation();
            List<ProcessedData> processedDataList = new ArrayList<>();
            long timeInterval = 10000;

            for (Map<String, ImuValues> imuMap : payload.getImu()) {
                for (Map.Entry<String, ImuValues> entry : imuMap.entrySet()) {
                    long time = Long.parseLong(entry.getKey());
                    ImuValues imuValues = entry.getValue();
                    int k = imuValues.getAccel().size() / 3;

                    for (int i = 0; i < k; i++) {
                        int index = i * 3;
                        int locationIndex = i * 4;

                        double lat = (locationList != null && locationList.size() > locationIndex) ? locationList.get(locationIndex) : gnssData.getPosition().get(0);
                        double lon = (locationList != null && locationList.size() > locationIndex + 1) ? locationList.get(locationIndex + 1) : gnssData.getPosition().get(1);
                        double altitude = (locationList != null && locationList.size() > locationIndex + 2) ? locationList.get(locationIndex + 2) : gnssData.getAltitude();
                        double velocity = (locationList != null && locationList.size() > locationIndex + 3) ? locationList.get(locationIndex + 3) : gnssData.getVelocity();

                        ProcessedData data = new ProcessedData.Builder()
                                .sensorId(sensorId)
                                .phoneNum(phoneNum)
                                .time(time + (long)(i * (timeInterval / (double)k)))
                                .accel(imuValues.getAccel().get(index), imuValues.getAccel().get(index + 1), imuValues.getAccel().get(index + 2))
                                .gyro(imuValues.getGyro().get(index), imuValues.getGyro().get(index + 1), imuValues.getGyro().get(index + 2))
                                .attitude(imuValues.getAttitude().get(index), imuValues.getAttitude().get(index + 1))
                                .location(lat, lon)
                                .gnss(velocity, altitude, gnssData.getBearing())
                                .travel(travelData.getTime(), travelData.getDistance())
                                .build();
                        processedDataList.add(data);
                    }
                }
            }
            return processedDataList;
        } catch (Exception e) {
            System.err.println("Error processing LTE V2 data: " + e.getMessage());
            return Collections.emptyList();
        }
    }
}
