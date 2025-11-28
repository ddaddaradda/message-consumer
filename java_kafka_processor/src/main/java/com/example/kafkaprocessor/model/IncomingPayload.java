package com.example.kafkaprocessor.model;

import com.google.gson.annotations.SerializedName;
import java.util.List;
import java.util.Map;

/**
 * Represents the top-level structure of the incoming JSON payload.
 * This class includes all possible fields from different data types (BLE, LTE, etc.).
 * Fields will be null if they are not present in a specific payload.
 */
public class IncomingPayload {
    @SerializedName("TITLE")
    private String title;

    @SerializedName("IMU")
    private List<Map<String, ImuValues>> imu;

    @SerializedName("GNSS")
    private GnssData gnss;

    @SerializedName("TRAVEL")
    private TravelData travel;

    @SerializedName("TIME")
    private Long time; // For Nonesub data

    @SerializedName("LOCATION")
    private List<Double> location; // For LTE V2 data

    // Getters
    public String getTitle() { return title; }
    public List<Map<String, ImuValues>> getImu() { return imu; }
    public GnssData getGnss() { return gnss; }
    public TravelData getTravel() { return travel; }
    public Long getTime() { return time; }
    public List<Double> getLocation() { return location; }

    // Convenience methods to check data type
    public boolean isLteType() {
        return travel != null;
    }

    public boolean isLteV2Type() {
        return isLteType() && location != null;
    }

    public boolean isBleType() {
        return imu != null && gnss != null && travel == null;
    }

    public boolean isNonesubType() {
        return time != null && gnss != null && imu == null;
    }
}
