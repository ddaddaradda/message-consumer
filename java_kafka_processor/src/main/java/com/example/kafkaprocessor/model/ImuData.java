package com.example.kafkaprocessor.model;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * Represents the values (ACCEL, GYRO, ATTITUDE) associated with a single IMU timestamp.
 */
public class ImuValues {
    @SerializedName("ACCEL")
    private List<Double> accel; // Using Double for broader compatibility with LTE data
    @SerializedName("GYRO")
    private List<Double> gyro;   // Using Double for broader compatibility
    @SerializedName("ATTITUDE")
    private List<Double> attitude;

    // Getters
    public List<Double> getAccel() { return accel; }
    public List<Double> getGyro() { return gyro; }
    public List<Double> getAttitude() { return attitude; }
}