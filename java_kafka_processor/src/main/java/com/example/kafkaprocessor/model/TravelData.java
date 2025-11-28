package com.example.kafkaprocessor.model;

import com.google.gson.annotations.SerializedName;

public class TravelData {
    @SerializedName("TIME")
    private long time;
    @SerializedName("DISTANCE")
    private long distance;

    // Getters
    public long getTime() { return time; }
    public long getDistance() { return distance; }
}
