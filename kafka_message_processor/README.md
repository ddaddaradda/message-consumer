# Kafka Message Processor (Python)

Kafka를 사용하여 라이더 센서 데이터를 수신, 처리 및 재전송하는 Python 기반 메시지 처리 시스템입니다.

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [시스템 아키텍처](#시스템-아키텍처)
- [설치 및 실행](#설치-및-실행)
- [설정](#설정)
- [프로젝트 구조](#프로젝트-구조)
- [메시지 처리 로직](#메시지-처리-로직)

## 개요

이 프로젝트는 RabbitMQ 기반 `riderLogMQReceiver`를 Kafka로 마이그레이션한 버전입니다. Kafka Consumer를 통해 소스 토픽에서 센서 데이터를 수신하고, 데이터 타입별로 처리한 후, 목적지 토픽으로 전송합니다.

## 주요 기능

### 1. Kafka 기반 메시지 스트리밍
- Kafka Consumer로 실시간 메시지 수신
- Kafka Producer로 처리된 데이터 전송
- 자동 오프셋 커밋 및 컨슈머 그룹 관리

### 2. 다중 데이터 타입 처리
- **BLE 데이터**: 블루투스 센서 데이터 파싱
- **LTE V1 데이터**: LTE 센서 데이터 파싱 (5초 주기)
- **LTE V2 데이터**: 향상된 LTE 센서 데이터 (10초 주기, LOCATION 필드 지원)
- **Nonesub 데이터**: 비구독 사용자 위치 데이터

### 3. 자동 메시지 디스패칭
- 페이로드 구조 기반 자동 타입 감지
- 각 데이터 타입에 맞는 프로세서 자동 선택
- 에러 핸들링 및 로깅

### 4. 확장 가능한 아키텍처
- 모듈화된 설계 (consumer, processor, producer 분리)
- 새로운 데이터 타입 추가 용이
- 설정 파일 기반 구성

## 시스템 아키텍처

```
[Kafka Source Topic]
        ↓
[Kafka Consumer]
        ↓
[Processor Dispatcher]
        ↓
[Type-Specific Processors]
  - BLE Processor
  - LTE Processor
  - LTE V2 Processor
  - Nonesub Processor
        ↓
[Kafka Producer]
        ↓
[Kafka Destination Topic]
```

### 메시지 흐름
1. Kafka Consumer가 `source_topic`에서 메시지를 읽음
2. `dispatch_processor()`가 페이로드 구조를 분석하여 타입 결정
3. 타입별 프로세서가 데이터를 파싱 및 변환
4. 처리된 데이터를 리스트로 반환
5. Kafka Producer가 각 데이터를 `destination_topic`으로 전송

## 설치 및 실행

### 필요 조건
- Python 3.8+
- Kafka 브로커 (실행 중이어야 함)
- kafka-python 라이브러리

### 설치

```bash
# 의존성 설치
uv pip install -r requirements.txt
```

### 설정 수정

`config/settings.py` 파일에서 Kafka 브로커 및 토픽 설정:

```python
# Kafka settings
KAFKA_BROKERS = ['localhost:9092']  # Kafka 브로커 주소
SOURCE_TOPIC = 'source_topic'        # 수신할 토픽
DESTINATION_TOPIC = 'destination_topic'  # 전송할 토픽
CONSUMER_GROUP_ID = 'my-group'       # 컨슈머 그룹 ID
```

### 실행

```bash
# Consumer 실행
uv run python run.py
```

## 설정

### `config/settings.py`

| 설정 항목 | 설명 | 기본값 |
|-----------|------|--------|
| `KAFKA_BROKERS` | Kafka 브로커 주소 리스트 | `['localhost:9092']` |
| `SOURCE_TOPIC` | 소스 토픽 이름 | `'source_topic'` |
| `DESTINATION_TOPIC` | 목적지 토픽 이름 | `'destination_topic'` |
| `CONSUMER_GROUP_ID` | Kafka 컨슈머 그룹 ID | `'my-group'` |

### Kafka Consumer 설정

```python
consumer = KafkaConsumer(
    SOURCE_TOPIC,
    bootstrap_servers=KAFKA_BROKERS,
    auto_offset_reset='earliest',  # 가장 이른 오프셋부터 읽기
    enable_auto_commit=True,       # 자동 오프셋 커밋
    group_id=CONSUMER_GROUP_ID,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
```

## 프로젝트 구조

```
kafka_message_processor/
├── config/
│   ├── __init__.py
│   └── settings.py          # Kafka 브로커, 토픽 등 설정
├── kafka_consumer/
│   ├── __init__.py
│   ├── consumer.py          # Kafka Consumer 메인 로직
│   ├── processor.py         # 데이터 타입별 처리 로직
│   └── producer.py          # Kafka Producer
├── run.py                   # 애플리케이션 진입점
├── requirements.txt         # Python 의존성
└── README.md                # 이 문서
```

### 주요 파일 설명

#### `consumer.py`
- `run_consumer()`: Kafka Consumer 실행 및 메시지 처리 루프
- 메시지를 수신하여 프로세서에 전달
- 처리된 데이터를 Producer로 전송

#### `processor.py`
메시지 타입별 처리 함수:
- `process_ble_data()`: BLE 센서 데이터 파싱
- `process_lte_data()`: LTE V1 센서 데이터 파싱
- `process_lte_v2_data()`: LTE V2 센서 데이터 파싱 (LOCATION 필드 지원)
- `process_nonesub_data()`: 비구독 사용자 데이터 파싱
- `dispatch_processor()`: 페이로드 구조 기반 자동 프로세서 선택

#### `producer.py`
- `get_producer()`: Kafka Producer 인스턴스 생성
- `send_message()`: 처리된 데이터를 Kafka로 전송

#### `settings.py`
- Kafka 브로커 주소
- 소스 및 목적지 토픽 이름
- 컨슈머 그룹 ID

## 메시지 처리 로직

### 1. 메시지 타입 자동 감지

`dispatch_processor()` 함수는 페이로드의 키를 확인하여 타입을 결정합니다:

```python
def dispatch_processor(payload):
    if "TRAVEL" in payload:
        if "LOCATION" in payload:
            return process_lte_v2_data(payload)  # LTE V2
        else:
            return process_lte_data(payload)      # LTE V1
    elif "IMU" in payload and "GNSS" in payload:
        return process_ble_data(payload)          # BLE
    elif "TIME" in payload and "GNSS" in payload:
        return process_nonesub_data(payload)      # Nonesub
    else:
        return None  # 알 수 없는 타입
```

### 2. 데이터 변환 예시

#### BLE 데이터 처리
```python
# 입력:
{
  "TITLE": "sensor123_01012345678_20240101",
  "IMU": [{"1234567890000": {"ACCEL": [100, 200, 16000], "GYRO": [10, 20, 30], "ATTITUDE": [0.1, 0.2]}}],
  "GNSS": {"POSITION": [37.5, 127.0], "VELOCITY": 30, "ALTITUDE": 100, "BEARING": 45}
}

# 출력:
[
  {
    "sensor_id": "sensor123",
    "phone_num": "01012345678",
    "time": 1234567890000,
    "ACCEL_X": 100,
    "ACCEL_Y": 200,
    "ACCEL_Z": 16000,
    "GYRO_X": 10,
    "GYRO_Y": 20,
    "GYRO_Z": 30,
    "PITCH": 0.1,
    "ROLL": 0.2,
    "LAT": 37.5,
    "LON": 127.0,
    "VELOCITY": 30,
    "ALTITUDE": 100,
    "BEARING": 45
  }
]
```

#### LTE V1 데이터 처리
- `time_interval = 5000ms` (5초 주기)
- IMU 배열을 3개씩 묶어서 분할
- 각 데이터 포인트에 시간 간격을 균등 분배

#### LTE V2 데이터 처리
- `time_interval = 10000ms` (10초 주기)
- `LOCATION` 필드가 있으면 개별 위치 정보 사용
- IMU 배열을 3개씩, LOCATION 배열을 4개씩 분할

### 3. 에러 핸들링

각 프로세서는 try-except 블록으로 에러를 캐치하고 로그를 출력합니다:

```python
try:
    # 데이터 처리 로직
    ...
except Exception as e:
    print(f"Error processing BLE data: {e}")
    return None
```

## 데이터 타입별 처리 특징

| 데이터 타입 | 시간 간격 | 특징 |
|------------|----------|------|
| **BLE** | 실시간 | 개별 IMU 데이터 포인트, 단일 GNSS 값 |
| **LTE V1** | 5초 | IMU 배열 (3의 배수), TRAVEL 정보 포함 |
| **LTE V2** | 10초 | LTE V1 + LOCATION 배열 (4의 배수) |
| **Nonesub** | 단일 | GNSS만 포함, IMU 없음 |

## RabbitMQ 버전과의 차이점

| 항목 | RabbitMQ 버전 | Kafka 버전 |
|------|--------------|-----------|
| **메시지 브로커** | RabbitMQ | Kafka |
| **비동기 처리** | Celery Tasks | 동기 처리 (Consumer Loop) |
| **데이터 저장** | MongoDB 직접 저장 | Kafka Topic으로 전송 |
| **로그 파일** | 파일 시스템에 로그 저장 | 콘솔 로그 출력 |
| **에러 핸들링** | 파일 기반 에러 로그 | 콘솔 에러 로그 |

## 확장 및 개선 방안

### 1. 새로운 데이터 타입 추가
`processor.py`에 새 프로세서 함수를 추가하고 `dispatch_processor()`를 수정:

```python
def process_new_type_data(payload):
    """새로운 타입 데이터 처리"""
    # 처리 로직
    return processed_data_list

def dispatch_processor(payload):
    # 기존 로직...
    elif "NEW_KEY" in payload:
        return process_new_type_data(payload)
```

### 2. MongoDB 저장 추가
Consumer에서 MongoDB 클라이언트를 추가하여 저장 가능:

```python
from pymongo import MongoClient

client = MongoClient(MONGO_URI)
db = client['database_name']

# 처리된 데이터 저장
for data_item in processed_data:
    db[collection_name].insert_one(data_item)
```

### 3. 배치 처리
여러 메시지를 모아서 한 번에 전송:

```python
batch = []
for message in consumer:
    processed = dispatch_processor(message.value)
    batch.extend(processed)

    if len(batch) >= BATCH_SIZE:
        for item in batch:
            send_message(producer, item)
        batch = []
```

## 트러블슈팅

### Kafka 연결 실패
- Kafka 브로커가 실행 중인지 확인
- `config/settings.py`의 `KAFKA_BROKERS` 주소가 올바른지 확인

### 메시지가 처리되지 않음
- 소스 토픽에 메시지가 존재하는지 확인
- 컨슈머 그룹 오프셋 리셋 필요 시: `auto_offset_reset='earliest'`

### 알 수 없는 메시지 타입
- 콘솔에 "Unknown message type" 로그 확인
- 페이로드 구조를 확인하고 `dispatch_processor()` 로직 수정

## 관련 프로젝트

- **RabbitMQ 버전**: `riderLogMQReceiver`
- **Java Kafka 버전**: `java_kafka_processor`


