package com.example.kafkaprocessor.model;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class GnssData {
    @SerializedName("POSITION")
    private List<Double> position;
    @SerializedName("VELOCITY")
    private double velocity;
    @SerializedName("ALTITUDE")
    private double altitude;
    @SerializedName("BEARING")
    private double bearing;

    // Getters and Setters
    public List<Double> getPosition() { return position; }
    public double getVelocity() { return velocity; }
    public double getAltitude() { return altitude; }
    public double getBearing() { return bearing; }
}
