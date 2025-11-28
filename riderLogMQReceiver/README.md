# RiderLog MQ Receiver

RabbitMQ를 사용하여 라이더의 센서 데이터(BLE, LTE, Nonesub)를 수신하고 MongoDB에 저장하는 Celery 기반 메시지 처리 시스템입니다.

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [시스템 아키텍처](#시스템-아키텍처)
- [데이터 타입](#데이터-타입)
- [설치 및 실행](#설치-및-실행)
- [환경 변수](#환경-변수)
- [프로젝트 구조](#프로젝트-구조)

## 개요

이 프로젝트는 모바일 디바이스에서 수집된 라이더의 주행 데이터를 RabbitMQ를 통해 수신하고, 데이터 타입별로 처리하여 MongoDB에 저장하는 시스템입니다. Celery를 사용하여 비동기적으로 메시지를 처리하며, 사고 감지 기능을 포함하고 있습니다.

## 주요 기능

### 1. 멀티 타입 데이터 수신
- **BLE 데이터**: 블루투스 기반 센서 데이터
- **LTE 데이터**: LTE 통신 기반 센서 데이터 (V1, V2)
- **Nonesub 데이터**: 구독하지 않은 사용자의 위치 데이터

### 2. 실시간 데이터 처리
- Celery를 활용한 비동기 메시지 처리
- RabbitMQ 큐를 통한 안정적인 메시지 전달
- MongoDB를 활용한 날짜별 컬렉션 관리

### 3. 사고 감지 알고리즘
- 가속도계 및 자이로스코프 데이터 분석
- 낙상 방향 감지 (좌/우)
- 충격량 및 충격 각도 계산
- 사고 전 속도 분석

### 4. 에러 핸들링 및 로깅
- 데이터 타입별 로그 디렉터리 관리
- 에러 로그 자동 기록
- 페이로드 검증 및 예외 처리

## 시스템 아키텍처

```
[Mobile Device] → [RabbitMQ] → [Celery Workers] → [MongoDB]
                                      ↓
                                [Log Files]
```

### 메시지 흐름
1. 모바일 디바이스에서 센서 데이터를 RabbitMQ로 전송
2. Celery Worker가 큐에서 메시지를 가져옴
3. 데이터 타입별 Task 함수가 데이터를 파싱 및 검증
4. 처리된 데이터를 MongoDB에 저장
5. 성공/실패 로그를 파일에 기록

## 데이터 타입

### BLE 데이터 구조
```json
{
  "TITLE": "sensor_id_phone_num_date",
  "IMU": [{
    "timestamp": {
      "ACCEL": [x, y, z],
      "GYRO": [x, y, z],
      "ATTITUDE": [pitch, roll]
    }
  }],
  "GNSS": {
    "POSITION": [lat, lon],
    "VELOCITY": speed,
    "ALTITUDE": altitude,
    "BEARING": bearing
  }
}
```

### LTE 데이터 구조
```json
{
  "TITLE": "sensor_id_phone_num",
  "IMU": [{
    "timestamp": {
      "ACCEL": [x1, y1, z1, x2, y2, z2, ...],
      "GYRO": [x1, y1, z1, x2, y2, z2, ...],
      "ATTITUDE": [p1, r1, y1, p2, r2, y2, ...]
    }
  }],
  "GNSS": {
    "POSITION": [lat, lon],
    "VELOCITY": speed,
    "ALTITUDE": altitude,
    "BEARING": bearing
  },
  "TRAVEL": {
    "TIME": travel_time,
    "DISTANCE": distance
  }
}
```

### LTE V2 데이터 구조
LTE 데이터 구조에 추가로 `LOCATION` 필드를 포함:
```json
{
  ...,
  "LOCATION": [lat1, lon1, alt1, vel1, lat2, lon2, alt2, vel2, ...]
}
```

### Nonesub 데이터 구조
```json
{
  "TITLE": "phone_num_date",
  "GNSS": {
    "POSITION": [lat, lon],
    "VELOCITY": speed,
    "ALTITUDE": altitude,
    "BEARING": bearing
  },
  "TIME": timestamp
}
```

## 설치 및 실행

### 필요 조건
- Python 3.8+
- RabbitMQ
- MongoDB (DocumentDB)
- Celery

### 설치

```bash
# 의존성 설치
uv pip install celery pymongo pandas numpy

# 또는 requirements.txt가 있는 경우
uv pip install -r requirements.txt
```

### 환경 변수 설정

`.env` 파일을 생성하고 다음 환경 변수를 설정합니다:

```env
# MongoDB 설정
DOCDB_URI=mongodb://username:password@host:port/database
TLSCA_path=/path/to/tls/certificate.pem

# RabbitMQ 설정
AMQPS_URI=amqps://username:password@host:port/vhost
```

### Celery Worker 실행

```bash
# 기본 실행
celery -A riderLogMQReceiver.celery worker --loglevel=info

# 다중 워커 실행
celery -A riderLogMQReceiver.celery worker --loglevel=info --concurrency=4

# 특정 큐만 처리
celery -A riderLogMQReceiver.celery worker --loglevel=info -Q ble_queue,lte_queue
```

## 환경 변수

| 변수명 | 설명 | 필수 여부 |
|--------|------|-----------|
| `DOCDB_URI` | MongoDB 연결 URI | 필수 |
| `TLSCA_path` | TLS 인증서 경로 | 필수 (DocumentDB 사용 시) |
| `AMQPS_URI` | RabbitMQ AMQPS 연결 URI | 필수 |

## 프로젝트 구조

```
riderLogMQReceiver/
├── accident_detection.py    # 사고 감지 알고리즘
├── celery.py                # Celery 앱 설정 및 MongoDB 연결
├── config.py                # 설정 클래스 (환경 변수, 로그 디렉터리)
├── tasks.py                 # Celery Task 정의 (BLE, LTE, LTE_V2, Nonesub)
└── README.md                # 이 문서
```

### 주요 파일 설명

#### `config.py`
- 환경 변수 로드
- MongoDB 및 RabbitMQ 설정
- 로그 디렉터리 구조 정의
- 로그 디렉터리 자동 생성

#### `celery.py`
- Celery 앱 초기화
- MongoDB 클라이언트 설정
- 데이터베이스 및 컬렉션 정의

#### `tasks.py`
- `receiveBLE_Data`: BLE 센서 데이터 처리
- `receiveLTE_Data`: LTE 센서 데이터 처리 (V1)
- `receiveLTE_V2_Data`: LTE 센서 데이터 처리 (V2, LOCATION 필드 지원)
- `receiveNonesub_Data`: 비구독 사용자 위치 데이터 처리

#### `accident_detection.py`
- `accident_detect()`: 센서 데이터 기반 사고 감지
- 가속도 및 자이로 임계값 기반 낙상 판단
- 충격량 계산 및 낙상 방향 분석
- 로그 파일 기록

## 로그 디렉터리

```
/home/ubuntu/log/
├── BLE/               # BLE 데이터 수신 로그
├── BLE_ERROR/         # BLE 에러 로그
├── LTE/               # LTE 데이터 수신 로그
├── LTE_ERROR/         # LTE 에러 로그
├── Nonesub/           # Nonesub 데이터 수신 로그
└── Nonesub_ERROR/     # Nonesub 에러 로그
```

## 사고 감지 알고리즘

### 감지 조건
- `|ACCEL_X| > 16384` (약 1G)
- `|GYRO_Y| > 3000` (deg/s)
- `ACCEL_Z < 16384`

### 계산 항목
1. **낙상 방향**: GYRO_Y 및 ACCEL_X 부호 분석
2. **충격량**: 3축 가속도 벡터의 크기
3. **충격 각도**: ACCEL_X와 ACCEL_Y의 아크탄젠트
4. **사고 전 속도**: 최대 속도 및 평균 속도

## Kafka 마이그레이션 안내

이 프로젝트는 RabbitMQ 기반으로 동작합니다. Kafka로 마이그레이션하려면 다음 프로젝트를 참고하세요:

- **Python 버전**: `kafka_message_processor`
- **Java 버전**: `java_kafka_processor`

