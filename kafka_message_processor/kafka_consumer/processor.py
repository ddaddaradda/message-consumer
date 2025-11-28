"""
Message Processor
"""
import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def process_ble_data(payload):
    """Processes BLE data payload."""
    try:
        TITLE = payload["TITLE"]
        sensor_id, phone_num, date = TITLE.split("_")
        imu_data_list = payload["IMU"]
        gnss_data = payload["GNSS"]
        processed_data_list = []
        for imu_data in imu_data_list:
            for time, imu_values in imu_data.items():
                data = {
                    "sensor_id": sensor_id,
                    "phone_num": phone_num,
                    "time": int(time),
                    "ACCEL_X": imu_values["ACCEL"][0],
                    "ACCEL_Y": imu_values["ACCEL"][1],
                    "ACCEL_Z": imu_values["ACCEL"][2],
                    "GYRO_X": imu_values["GYRO"][0],
                    "GYRO_Y": imu_values["GYRO"][1],
                    "GYRO_Z": imu_values["GYRO"][2],
                    "PITCH": imu_values["ATTITUDE"][0],
                    "ROLL": imu_values["ATTITUDE"][1],
                    "LAT": gnss_data["POSITION"][0],
                    "LON": gnss_data["POSITION"][1],
                    "VELOCITY": gnss_data["VELOCITY"],
                    "ALTITUDE": gnss_data["ALTITUDE"],
                    "BEARING": gnss_data["BEARING"],
                }
                processed_data_list.append(data)
        return processed_data_list
    except Exception as e:
        logger.error(f"Error processing BLE data: {e}", exc_info=True)
        return None

def process_lte_data(payload):
    """Processes LTE data payload."""
    try:
        TITLE = payload["TITLE"]
        sensor_id, phone_num = TITLE.split("_")
        imu_data_list = payload["IMU"]
        gnss_data = payload["GNSS"]
        travel_data = payload["TRAVEL"]
        processed_data_list = []
        time_interval = 5000
        for imu_data in imu_data_list:
            for time, imu_values in imu_data.items():
                k = len(imu_values['ACCEL']) // 3
                for i in range(k):
                    index = i * 3
                    data = {
                        "sensor_id": sensor_id,
                        "phone_num": phone_num,
                        "time": int(int(time) + i * (time_interval / k)),
                        "ACCEL_X": imu_values["ACCEL"][index],
                        "ACCEL_Y": imu_values["ACCEL"][index + 1],
                        "ACCEL_Z": imu_values["ACCEL"][index + 2],
                        "GYRO_X": imu_values["GYRO"][index],
                        "GYRO_Y": imu_values["GYRO"][index + 1],
                        "GYRO_Z": imu_values["GYRO"][index + 2],
                        "PITCH": imu_values["ATTITUDE"][index],
                        "ROLL": imu_values["ATTITUDE"][index + 1],
                        "LAT": gnss_data["POSITION"][0],
                        "LON": gnss_data["POSITION"][1],
                        "VELOCITY": gnss_data["VELOCITY"],
                        "ALTITUDE": gnss_data["ALTITUDE"],
                        "BEARING": gnss_data["BEARING"],
                        "TIME": travel_data["TIME"],
                        "DISTANCE": travel_data["DISTANCE"],
                    }
                    processed_data_list.append(data)
        return processed_data_list
    except Exception as e:
        logger.error(f"Error processing LTE data: {e}", exc_info=True)
        return None

def process_lte_v2_data(payload):
    """Processes LTE V2 data payload."""
    try:
        TITLE = payload["TITLE"]
        sensor_id, phone_num = TITLE.split("_")
        imu_data_list = payload["IMU"]
        gnss_data = payload["GNSS"]
        travel_data = payload["TRAVEL"]
        processed_data_list = []
        time_interval = 10000
        for imu_data in imu_data_list:
            for time, imu_values in imu_data.items():
                k = len(imu_values['ACCEL']) // 3
                lat = gnss_data["POSITION"][0]
                lon = gnss_data["POSITION"][1]
                velocity = gnss_data["VELOCITY"]
                altitude = gnss_data["ALTITUDE"]
                for i in range(k):
                    index = i * 3
                    location_index = i * 4
                    if "LOCATION" in payload:
                        location_list = payload["LOCATION"]
                        lat = location_list[location_index]
                        lon = location_list[location_index + 1]
                        altitude = location_list[location_index + 2]
                        velocity = location_list[location_index + 3]
                    data = {
                        "sensor_id": sensor_id,
                        "phone_num": phone_num,
                        "time": int(int(time) + i * (time_interval / k)),
                        "ACCEL_X": imu_values["ACCEL"][index],
                        "ACCEL_Y": imu_values["ACCEL"][index + 1],
                        "ACCEL_Z": imu_values["ACCEL"][index + 2],
                        "GYRO_X": imu_values["GYRO"][index],
                        "GYRO_Y": imu_values["GYRO"][index + 1],
                        "GYRO_Z": imu_values["GYRO"][index + 2],
                        "PITCH": imu_values["ATTITUDE"][index],
                        "ROLL": imu_values["ATTITUDE"][index + 1],
                        "LAT": lat,
                        "LON": lon,
                        "VELOCITY": velocity,
                        "ALTITUDE": altitude,
                        "BEARING": gnss_data["BEARING"],
                        "TIME": travel_data["TIME"],
                        "DISTANCE": travel_data["DISTANCE"],
                    }
                    processed_data_list.append(data)
        return processed_data_list
    except Exception as e:
        logger.error(f"Error processing LTE V2 data: {e}", exc_info=True)
        return None

def process_nonesub_data(payload):
    """Processes Nonesub data payload."""
    try:
        TITLE = payload["TITLE"]
        phone_num, date = TITLE.split("_")
        gnss_data = payload["GNSS"]
        time = payload["TIME"]
        data = {
            "phone_num": phone_num,
            "time": int(time),
            "LAT": gnss_data["POSITION"][0],
            "LON": gnss_data["POSITION"][1],
            "VELOCITY": gnss_data["VELOCITY"],
            "ALTITUDE": gnss_data["ALTITUDE"],
            "BEARING": gnss_data["BEARING"],
        }
        return [data]  # Return as a list for consistency
    except Exception as e:
        logger.error(f"Error processing Nonesub data: {e}", exc_info=True)
        return None

def dispatch_processor(payload):
    """
    Dispatches the payload to the correct processor based on its structure.
    """
    # A more robust solution would be to have a 'type' field in the message.
    # This dispatch logic is based on the key structures observed in tasks.py.
    if "TRAVEL" in payload:
        # Differentiate between LTE and LTE_V2 by checking for the 'LOCATION' key.
        if "LOCATION" in payload:
            return process_lte_v2_data(payload)
        else:
            return process_lte_data(payload)
    elif "IMU" in payload and "GNSS" in payload:
        return process_ble_data(payload)
    elif "TIME" in payload and "GNSS" in payload:
        return process_nonesub_data(payload)
    else:
        logger.warning(f"Unknown message type. Payload: {json.dumps(payload)}")
        return None