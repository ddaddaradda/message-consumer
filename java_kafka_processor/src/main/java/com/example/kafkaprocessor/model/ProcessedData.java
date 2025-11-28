package com.example.kafkaprocessor.model;

/**
 * Represents the final processed data structure to be sent to the destination Kafka topic.
 * This is a "flattened" version of the incoming data.
 */
public class ProcessedData {
    private String sensorId;
    private String phoneNum;
    private long time;
    private Double accelX;
    private Double accelY;
    private Double accelZ;
    private Double gyroX;
    private Double gyroY;
    private Double gyroZ;
    private Double pitch;
    private Double roll;
    private Double lat;
    private Double lon;
    private Double velocity;
    private Double altitude;
    private Double bearing;
    private Long travelTime; // from TRAVEL.TIME
    private Long travelDistance; // from TRAVEL.DISTANCE

    // Using a builder pattern for easier construction
    public static class Builder {
        private ProcessedData data = new ProcessedData();

        public Builder sensorId(String sensorId) {
            data.sensorId = sensorId;
            return this;
        }

        public Builder phoneNum(String phoneNum) {
            data.phoneNum = phoneNum;
            return this;
        }

        public Builder time(long time) {
            data.time = time;
            return this;
        }

        public Builder accel(double x, double y, double z) {
            data.accelX = x;
            data.accelY = y;
            data.accelZ = z;
            return this;
        }

        public Builder gyro(double x, double y, double z) {
            data.gyroX = x;
            data.gyroY = y;
            data.gyroZ = z;
            return this;
        }

        public Builder attitude(double pitch, double roll) {
            data.pitch = pitch;
            data.roll = roll;
            return this;
        }

        public Builder location(double lat, double lon) {
            data.lat = lat;
            data.lon = lon;
            return this;
        }
        
        public Builder gnss(double velocity, double altitude, double bearing) {
            data.velocity = velocity;
            data.altitude = altitude;
            data.bearing = bearing;
            return this;
        }

        public Builder travel(long time, long distance) {
            data.travelTime = time;
            data.travelDistance = distance;
            return this;
        }

        public ProcessedData build() {
            return data;
        }
    }

    // Getters for Gson serialization
    public String getSensorId() { return sensorId; }
    public String getPhoneNum() { return phoneNum; }
    public long getTime() { return time; }
    public Double getAccelX() { return accelX; }
    public Double getAccelY() { return accelY; }
    public Double getAccelZ() { return accelZ; }
    public Double getGyroX() { return gyroX; }
    public Double getGyroY() { return gyroY; }
    public Double getGyroZ() { return gyroZ; }
    public Double getPitch() { return pitch; }
    public Double getRoll() { return roll; }
    public Double getLat() { return lat; }
    public Double getLon() { return lon; }
    public Double getVelocity() { return velocity; }
    public Double getAltitude() { return altitude; }
    public Double getBearing() { return bearing; }
    public Long getTravelTime() { return travelTime; }
    public Long getTravelDistance() { return travelDistance; }
}
