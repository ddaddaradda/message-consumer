from __future__ import absolute_import
from datetime import datetime
import pandas as pd
import os
import json
from celery import current_task

from .celery import app, Doc_BLE, Doc_LTE, Doc_Nonesub
from .config import Config

# Initialize logging directories
Config.ensure_log_dirs()


@app.task
def receiveBLE_Data(payload):
    today = datetime.today().strftime("%Y%m%d")
    try:
        # Validate payload structure
        if not all(key in payload for key in ["TITLE", "IMU", "GNSS"]):
            raise ValueError("Missing required fields in payload")
            
        TITLE = payload["TITLE"]
        try:
            sensor_id, phone_num, date = TITLE.split("_")  # TITLE = {sensor_id}_{phone_num}_{date}
        except ValueError:
            raise ValueError("Invalid TITLE format")
            
        # Log incoming data
        log_path = os.path.join(Config.LOG_DIRS['ble'], f"{today}_{sensor_id}_{phone_num}.txt")
        with open(log_path, "a") as file:
            file.write(f"{datetime.today()}\n{json.dumps(payload)}\n")
            
        imu_data_list = payload["IMU"]
        gnss_data = payload["GNSS"]
        bulk_insert_data = []
        for imu_data in imu_data_list:
            for time, imu_values in imu_data.items(): # BLE payload 예시 dict_items([('1688530356264', {'ACCEL': [398, -434, 16346], 'GYRO': [-4, -4, -2], 'ATTITUDE': [0, 0]})])
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
                bulk_insert_data.append(data)
        col = Doc_BLE[date]
        col.insert_many(bulk_insert_data)
    except Exception as e:
        error_log_path = os.path.join(Config.LOG_DIRS['ble_error'], f"error_{today}.txt")
        with open(error_log_path, "a") as file:
            file.write(f"{datetime.today()}\nError: {str(e)}\nPayload: {json.dumps(payload)}\n")
        raise  # Re-raise the exception for Celery to handle


@app.task
def receiveLTE_Data(payload):
    """
    LTE payload 예시 
    {
        "TITLE":"number","IMU":[{"1695144213683":{"ACCEL":[-138,106,16150,-138,106,16150],
        "GYRO":[-32,7,43,-32,7,43],"ATTITUDE":[-0.36485,-0.48589,0.001549,-0.36485,-0.48589,0.001549]}}],
        "GNSS":{"POSITION":[37.60815,126.896439],"VELOCITY":0,"ALTITUDE":0,"BEARING":0}
        "TRAVEL":{"TIME":0, "DISTANCE":0}
    }
    """
    today = datetime.today().strftime("%Y%m%d")

    try :
        # Validate payload structure
        if not all(key in payload for key in ["TITLE", "IMU", "GNSS", "TRAVEL"]):
            raise ValueError("Missing required fields in payload")

        TITLE = payload["TITLE"]
        try:
            sensor_id, phone_num = TITLE.split("_")
        except ValueError:
            raise ValueError("Invalid TITLE format")

        imu_data_list = payload["IMU"]
        gnss_data = payload["GNSS"]
        travel_data = payload["TRAVEL"]
        bulk_insert_data = []
        # LTE 주기 시간에 따라 time_interval 설정
        time_interval = 5000
        for imu_data in imu_data_list:
            for time, imu_values in imu_data.items():
                date=datetime.fromtimestamp(float(time) / 1000).strftime('%Y%m%d')
                k = len(imu_values['ACCEL'])//3
                for i in range(k): 
                    index = i * 3
                    data = {
                        "sensor_id": sensor_id,
                        "phone_num": phone_num,  # fixed phone_num: 01012345678
                        "time": int(int(time) + i*(time_interval/k)),
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
                    bulk_insert_data.append(data)
        if len(bulk_insert_data) == 0 :
            pass
        else :
            col = Doc_LTE[date]
            # col.insert_many(bulk_insert_data)
            from itertools import islice
            from pymongo import WriteConcern

            def chunks(data, size=25):
                it = iter(data)
                for chunk in iter(lambda: tuple(islice(it, size)), ()):
                    yield chunk

            # 25개씩 나누어 write concern을 낮춘 후 insert_many로 배치 삽입
            for batch in chunks(bulk_insert_data, size=25):
                col.with_options(write_concern=WriteConcern(w=1, j=False)).insert_many(batch)
            # try :
            #     col_total = Doc_LTE['LTE_total']
            #     # col_test.insert_many(bulk_insert_data)
            #     # 25개씩 나누어 write concern을 낮춘 후 insert_many로 배치 삽입
            #     for batch in chunks(bulk_insert_data, size=25):
            #         col_total.with_options(write_concern=WriteConcern(w=1, j=False)).insert_many(batch)      
            # except :
            #     pass
    except Exception as e:
        error_log_path = os.path.join(Config.LOG_DIRS['lte_error'], f"error_{today}.txt")
        with open(error_log_path, "a") as file:
            file.write(f"{datetime.today()}\nError: {str(e)}\nPayload: {json.dumps(payload)}\n")
        raise  # Re-raise the exception for Celery to handle


@app.task
def receiveLTE_V2_Data(payload):
    """
    LTE payload 예시 
    {
        "TITLE":"number","IMU":[{"1695144213683":{"ACCEL":[-138,106,16150,-138,106,16150],
        "GYRO":[-32,7,43,-32,7,43],"ATTITUDE":[-0.36485,-0.48589,0.001549,-0.36485,-0.48589,0.001549]}}],
        "GNSS":{"POSITION":[37.60815,126.896439],"VELOCITY":0,"ALTITUDE":0,"BEARING":0}
        "TRAVEL":{"TIME":0, "DISTANCE":0}
    }
    """  
    today = datetime.today().strftime("%Y%m%d")
    exchange = current_task.request.delivery_info.get('exchange')

    try :
        TITLE = payload["TITLE"]
        sensor_id, phone_num = TITLE.split("_") 
        imu_data_list = payload["IMU"]
        gnss_data = payload["GNSS"]
        travel_data = payload["TRAVEL"]
        bulk_insert_data = []
        # LTE 주기 시간에 따라 time_interval 설정
        time_interval = 10000
        for imu_data in imu_data_list:
            for time, imu_values in imu_data.items():
                date=datetime.fromtimestamp(float(time) / 1000).strftime('%Y%m%d')
                k = len(imu_values['ACCEL'])//3
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
                        "phone_num": phone_num,  # fixed phone_num: 01012345678
                        "time": int(int(time) + i*(time_interval/k)),
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
                    bulk_insert_data.append(data)      

        if len(bulk_insert_data) == 0 :
            pass
        else :
            col = Doc_LTE[date]
            # col.insert_many(bulk_insert_data)
            from itertools import islice
            from pymongo import WriteConcern

            def chunks(data, size=25):
                it = iter(data)
                for chunk in iter(lambda: tuple(islice(it, size)), ()):
                    yield chunk
            # 25개씩 나누어 write concern을 낮춘 후 insert_many로 배치 삽입
            for batch in chunks(bulk_insert_data, size=25):
                col.with_options(write_concern=WriteConcern(w=1, j=False)).insert_many(batch)

                 
    except Exception as e:
        error_log_path = os.path.join(Config.LOG_DIRS['lte_error'], f"error_{today}.txt")
        with open(error_log_path, "a") as file:
            file.write(f"{datetime.today()}\nError: {str(e)}\nPayload: {json.dumps(payload)}\n")
        raise  # Re-raise the exception for Celery to handle



@app.task
def receiveNonesub_Data(payload):
    today = datetime.today().strftime("%Y%m%d")
    try:
        # Validate payload structure
        if not all(key in payload for key in ["TITLE", "GNSS", "TIME"]):
            raise ValueError("Missing required fields in payload")

        # Log incoming data
        log_path = os.path.join(Config.LOG_DIRS['nonesub'], f"Nonesub_{today}.txt")
        with open(log_path, "a") as file:
            file.write(f"{datetime.today()}\n{json.dumps(payload)}\n")

        TITLE = payload["TITLE"]
        try:
            phone_num, date = TITLE.split("_")  # TITLE = {phone_num}_{date}
        except ValueError:
            raise ValueError("Invalid TITLE format")

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
        col = Doc_Nonesub[today]
        col.insert_one(data)
    except Exception as e:
        error_log_path = os.path.join(Config.LOG_DIRS['nonesub_error'], f"error_{today}.txt")
        with open(error_log_path, "a") as file:
            file.write(f"{datetime.today()}\nError: {str(e)}\nPayload: {json.dumps(payload)}\n")
        raise  # Re-raise the exception for Celery to handle
