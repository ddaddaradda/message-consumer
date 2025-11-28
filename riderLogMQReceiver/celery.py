from celery import Celery

import pymongo
import sys
import os
from kafka import KafkaProducer
import json
print("Python Version:", sys.version)

AMQPS_URI = os.environ.get('AMQPS_URI')
DOCDB_URI = os.environ.get('DOCDB_URI')
TLSCA_path = os.environ.get('TLSCA_path')


app = Celery('riderLogMQReceiver',
            broker=AMQPS_URI,
            backend='rpc://',
            include=['riderLogMQReceiver.tasks'],
            broker_connection_retry=True,
            broker_connection_retry_on_startup=True,
            broker_connection_max_retries=10)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=False,
)

app.conf.timezone = 'Asia/Seoul'

# aws_DocumentDB
##Specify the database to be used
client = pymongo.MongoClient(host=DOCDB_URI,tls=True,tlsCAFile=TLSCA_path) 
# ble
Doc_BLE = client["BLE"] #BLE 데이터 베이스 선택
# lte
Doc_LTE = client["LTE"] #LTE 데이터 베이스 선택
# Nonesub
Doc_Nonesub = client["Nonesub"] #LTE 데이터 베이스 선택


if __name__ == '__main__':
    app.start()