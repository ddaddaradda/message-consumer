import pandas as pd
import numpy as np
from datetime import datetime
import os

def line_logging(*messages):
    today = datetime.now()
    log_time = today.strftime('[%Y/%m/%d %H:%M:%S]')
    log = [str(message) for message in messages]
    pid = os.getpid()
    log_line = f'{log_time}[PID: {pid}]:[' + ', '.join(log) + ']'
    log_file_name = f"log_{today.strftime('%Y%m%d')}.txt"
    with open(log_file_name, 'a') as log_file:
        log_file.write(log_line + '\n')


def accident_detect(data: pd.DataFrame):
    data['DATE'] = data['time'].apply(lambda x : datetime.fromtimestamp(x / 1000).strftime('%Y-%m-%d %H:%M:%S'))    
    sub_df = data[["DATE", "sensor_id", "VELOCITY", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X", "GYRO_Y", "GYRO_Z"]].copy()
    
    fallen_df = sub_df.loc[(abs(sub_df["ACCEL_X"]) > 16384) & (abs(sub_df["GYRO_Y"]) > 3000) & (sub_df["ACCEL_Z"] < 16384)]

    # (TODO) 차분한 센서의 데이터를 확인하여, 표준편차 이상의 변동을 가지는 데이터를 확인
    # 1. 해당 데이터의 GYRO, ACCEL 의 값이 기준치 이상인 경우 사고가 발생한 경우라고 판단할 수 있음
    # 2. 해당 사건의 인덱스를 추출할 수 있고 각 인덱스의 범위의 분석을 통해 실제 사고의 발생 부분을 추려 낼 수 있는 방법이 될 수 있음

    # 넘어짐 여부 판단(사고 데이터의특징으로 나타는 경우임)
    # 1 : Left, 2 : Right, 0 : Not Fallen

    if fallen_df.shape[0] > 0:
        line_logging(f'Sensor_ID : {sub_df["sensor_id"].unique()}')

        # 사고 시점
        accident_index = fallen_df.index[0]
        accident_time = sub_df.iloc[accident_index]["DATE"]

        line_logging(f"accident time : {accident_time}")

        # 넘어진 방향 판단
        if (fallen_df["GYRO_Y"].min() < -3000) & (fallen_df["ACCEL_X"].max() > 16384):
            fallen_direction = "LEFT"
            line_logging(f"falled direction : {fallen_direction}")
        elif (fallen_df["GYRO_Y"].max() > 3000) & (fallen_df["ACCEL_X"].min() < -16384):
            fallen_direction = "RIGHT"
            line_logging(f"falled direction : {fallen_direction}")
        else:
            fallen_direction = "None"
            line_logging(f"not fall")

        # 충격량
        impact_scalar_xyz = (sub_df.iloc[:].apply(lambda row: round(np.sqrt(row["ACCEL_X"] ** 2 + row["ACCEL_Y"] ** 2 + row["ACCEL_Z"] ** 2 ), 2, ), axis=1, ).max())
        impact_scalar_xy = (sub_df.iloc[:].apply(lambda row: round(np.sqrt(row["ACCEL_X"] ** 2 + row["ACCEL_Y"] ** 2), 2 ), axis=1,  ).max())

        line_logging(f"impact scalar xyz : {impact_scalar_xyz:,}")
        line_logging(f"impact scalar xz : {impact_scalar_xy:,}")

        # 사고 직전 속도
        before_accident_max_speed = sub_df.iloc[:]["VELOCITY"].max()
        before_accident_mean_speed = sub_df.iloc[:]["VELOCITY"].mean()
        line_logging( f"Before Accident Max Speed : {round(before_accident_max_speed,2)} km/h" )
        line_logging( f"Before Accident Mean Speed : {round(before_accident_mean_speed,2)} km/h" )

        impact_scalar_xyz_index = ( sub_df.iloc[:].apply( lambda row: round( np.sqrt( row["ACCEL_X"] ** 2 + row["ACCEL_Y"] ** 2 + row["ACCEL_Z"] ** 2 ),  2, ), axis=1, ).idxmax())
        impact_scalar_xy_index = ( sub_df.iloc[:].apply( lambda row: round( np.sqrt(row["ACCEL_X"] ** 2 + row["ACCEL_Y"] ** 2), 2 ), axis=1, ).idxmax() )
        line_logging(f"impact_scalar_xyz_max_index : {impact_scalar_xyz_index}")
        line_logging(f"impact_scalar_xy_index : {impact_scalar_xy_index}")

        # 충격 방향
        impact_degree = round(np.degrees( np.arctan2( sub_df.iloc[impact_scalar_xyz_index]["ACCEL_Y"], sub_df.iloc[impact_scalar_xyz_index]["ACCEL_X"], ) ), 2, )
        line_logging(f"Accident Impact Degree : {impact_degree}")
        
        # Slack Alram
        date = data["DATE"].dt.strftime("%Y-%m-%d").unique()[0].replace("-", "")
        sensor_id = data["ID"].unique()[0]
        message = f" {date} {sensor_id} 사고 발생"
        # slack_alram(message)
        line_logging(message)
        accident_info = [ tuple( [date, sensor_id, accident_time.strftime("%Y-%m-%d %H:%M:%S"), fallen_direction, impact_scalar_xyz, impact_scalar_xy, before_accident_max_speed, before_accident_mean_speed, impact_degree, ])]
        line_logging(accident_info)

    else:
        line_logging(f"*------- None Accident Sensor -------*")