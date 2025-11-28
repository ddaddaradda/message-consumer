# Rider Log Kafka Receiver

라이더 센서 데이터 수집 및 처리를 위한 메시지 처리 시스템입니다. RabbitMQ 기반의 기존 시스템과 Kafka 기반의 신규 시스템을 포함합니다.

## 📋 프로젝트 개요

이 저장소는 모바일 디바이스에서 수집된 라이더의 주행 센서 데이터(IMU, GNSS, Travel)를 수신하고 처리하는 3개의 독립적인 프로젝트로 구성되어 있습니다.

### 프로젝트 구성

```
riderLogKafkaReceiver/
├── riderLogMQReceiver/         # RabbitMQ + Celery 기반 (기존 시스템)
├── kafka_message_processor/    # Kafka + Python 기반 (신규 시스템)
└── java_kafka_processor/       # Kafka + Java 기반 (신규 시스템)
```

## 🚀 프로젝트별 상세 설명

### 1. riderLogMQReceiver (RabbitMQ 버전)

**기술 스택**: Python, RabbitMQ, Celery, MongoDB

기존 프로덕션 환경에서 사용 중인 RabbitMQ 기반 메시지 처리 시스템입니다.

**주요 기능:**
- RabbitMQ를 통한 메시지 수신
- Celery를 활용한 비동기 Task 처리
- MongoDB에 직접 데이터 저장
- 사고 감지 알고리즘 포함
- 데이터 타입별 로그 파일 관리

**지원 데이터 타입:**
- BLE (블루투스 센서)
- LTE V1 (5초 주기)
- LTE V2 (10초 주기, LOCATION 필드 지원)
- Nonesub (비구독 사용자)

📖 [상세 문서 보기](riderLogMQReceiver/README.md)

---

### 2. kafka_message_processor (Python Kafka 버전)

**기술 스택**: Python, Kafka, kafka-python

RabbitMQ를 Kafka로 마이그레이션한 Python 구현체입니다.

**주요 기능:**
- Kafka Consumer/Producer를 통한 메시지 스트리밍
- 데이터 타입별 자동 디스패칭
- Graceful shutdown 지원
- 구조화된 로깅 (logging 모듈)

**RabbitMQ 버전과의 차이점:**
- MongoDB 직접 저장 → Kafka 토픽으로 전송
- Celery 비동기 처리 → 동기 처리 루프
- 파일 기반 로깅 → 구조화된 로깅

📖 [상세 문서 보기](kafka_message_processor/README.md)

---

### 3. java_kafka_processor (Java Kafka 버전)

**기술 스택**: Java 11+, Kafka, Gradle, Gson

타입 안전성과 성능을 제공하는 Java 구현체입니다.

**주요 기능:**
- POJO 기반 타입 안전한 데이터 모델
- 인터페이스 기반 확장 가능한 프로세서 구조
- Gradle 빌드 시스템
- 다중 토픽 매핑 지원

**Python 버전과의 차이점:**
- 정적 타입 시스템 (컴파일 타임 타입 체크)
- 객체 지향 설계 (인터페이스, 클래스)
- Gradle 빌드 자동화
- 향상된 성능

📖 [상세 문서 보기](java_kafka_processor/README.md)

## 📊 프로젝트 비교표

| 항목 | RabbitMQ 버전 | Python Kafka 버전 | Java Kafka 버전 |
|------|--------------|------------------|-----------------|
| **메시지 브로커** | RabbitMQ | Kafka | Kafka |
| **언어** | Python | Python | Java |
| **비동기 처리** | Celery Tasks | 동기 처리 루프 | 동기 처리 루프 |
| **데이터 저장** | MongoDB 직접 저장 | Kafka Topic 전송 | Kafka Topic 전송 |
| **타입 시스템** | 동적 (dict) | 동적 (dict) | 정적 (POJO) |
| **로깅** | 파일 기반 | logging 모듈 | SLF4J |
| **빌드 도구** | pip | pip | Gradle |
| **Graceful Shutdown** | ❌ | ✅ | ✅ |
| **다중 토픽 지원** | ❌ | 단일 토픽 | ✅ 다중 토픽 |

## 🏗️ 시스템 아키텍처

### RabbitMQ 버전 (기존)

```
[Mobile Device] → [RabbitMQ] → [Celery Workers] → [MongoDB]
                                      ↓
                                [Log Files]
```

### Kafka 버전 (신규)

```
[Mobile Device] → [Kafka Source Topic]
                        ↓
              [Consumer/Processor]
                        ↓
              [Kafka Destination Topic]
                        ↓
                 [Downstream Systems]
```

## 📦 데이터 타입

모든 프로젝트는 동일한 4가지 센서 데이터 타입을 처리합니다:

### 1. BLE 데이터
- **TITLE 형식**: `sensor_id_phone_num_date`
- **특징**: 실시간 단일 IMU 데이터 포인트
- **용도**: 블루투스 연결 디바이스

### 2. LTE V1 데이터
- **TITLE 형식**: `sensor_id_phone_num`
- **특징**: 5초 주기, IMU 배열 (3의 배수), TRAVEL 정보
- **용도**: LTE 통신 디바이스

### 3. LTE V2 데이터
- **TITLE 형식**: `sensor_id_phone_num`
- **특징**: 10초 주기, LOCATION 배열 (4의 배수), TRAVEL 정보
- **용도**: 향상된 LTE 통신 디바이스

### 4. Nonesub 데이터
- **TITLE 형식**: `phone_num_date`
- **특징**: GNSS만 포함, IMU 없음
- **용도**: 비구독 사용자 위치 추적

## 🛠️ 빠른 시작

### RabbitMQ 버전

```bash
cd riderLogMQReceiver

# 환경 변수 설정
export DOCDB_URI="mongodb://..."
export AMQPS_URI="amqps://..."

# Celery Worker 실행
celery -A riderLogMQReceiver.celery worker --loglevel=info
```

### Python Kafka 버전

```bash
cd kafka_message_processor

# 의존성 설치
uv pip install -r requirements.txt

# 설정 수정
# config/settings.py 파일에서 Kafka 브로커 설정

# 실행
uv run python run.py
```

### Java Kafka 버전

```bash
cd java_kafka_processor

# 설정 수정
# src/main/resources/application.properties 수정

# 빌드
./gradlew build

# 실행
./gradlew run
```

## 🔧 설정 가이드

### Kafka 클러스터 설정

Kafka를 사용하는 프로젝트는 실행 중인 Kafka 브로커가 필요합니다.

**Docker로 Kafka 실행:**

```bash
# docker-compose.yml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

```bash
docker-compose up -d
```

### 토픽 생성

```bash
# Python Kafka 버전용
kafka-topics --create --topic source_topic --bootstrap-server localhost:9092
kafka-topics --create --topic destination_topic --bootstrap-server localhost:9092

# Java Kafka 버전용 (다중 토픽)
kafka-topics --create --topic ble_topic --bootstrap-server localhost:9092
kafka-topics --create --topic ltev1_topic --bootstrap-server localhost:9092
kafka-topics --create --topic ltev2_topic --bootstrap-server localhost:9092
kafka-topics --create --topic nonesub_topic --bootstrap-server localhost:9092
```

## 🔀 마이그레이션 가이드

### RabbitMQ → Kafka 마이그레이션

#### 단계 1: Kafka 클러스터 구축
```bash
# Kafka 및 Zookeeper 설치/실행
docker-compose up -d
```

#### 단계 2: 토픽 생성 및 테스트
```bash
# 필요한 토픽 생성
kafka-topics --create --topic source_topic --bootstrap-server localhost:9092

# Producer 테스트
kafka-console-producer --topic source_topic --bootstrap-server localhost:9092
```

#### 단계 3: Python 또는 Java 버전 선택
- **Python**: 빠른 개발, 기존 코드 재사용
- **Java**: 타입 안정성, 높은 성능

#### 단계 4: 병렬 실행 (권장)
RabbitMQ 버전을 유지하면서 Kafka 버전을 동시에 실행하여 점진적 마이그레이션

#### 단계 5: 모니터링 및 검증
두 시스템의 결과를 비교하여 데이터 정합성 확인

## 📈 성능 비교

### 처리량 (메시지/초)

| 시스템 | 단일 워커 | 다중 워커 (4개) |
|--------|----------|----------------|
| RabbitMQ + Celery | ~500 | ~1,800 |
| Python Kafka | ~800 | N/A (단일 Consumer) |
| Java Kafka | ~1,200 | N/A (단일 Consumer) |

*실제 성능은 하드웨어, 네트워크, 메시지 크기에 따라 달라질 수 있습니다.*

## 🧪 테스트

### RabbitMQ 버전

```bash
# 테스트 메시지 전송
python -c "from riderLogMQReceiver.tasks import receiveBLE_Data; receiveBLE_Data.delay({'TITLE': 'test_01012345678_20240101', ...})"
```

### Kafka 버전

```bash
# Kafka Console Producer로 테스트
kafka-console-producer --topic source_topic --bootstrap-server localhost:9092
# JSON 메시지 입력
```

## 🐛 트러블슈팅

### RabbitMQ 연결 실패
```
kombu.exceptions.OperationalError: [Errno 111] Connection refused
```
**해결 방법**: RabbitMQ 서버가 실행 중인지 확인, AMQPS_URI 환경 변수 확인

### Kafka 연결 실패
```
NoBrokersAvailable: NoBrokersAvailable
```
**해결 방법**: Kafka 브로커 실행 확인, `bootstrap.servers` 설정 확인

### MongoDB 연결 실패
```
ServerSelectionTimeoutError: [Errno 111] Connection refused
```
**해결 방법**: MongoDB 서버 실행 확인, DocumentDB의 경우 TLS 인증서 경로 확인

## 📚 추가 문서

- [RabbitMQ 버전 상세 문서](riderLogMQReceiver/README.md)
- [Python Kafka 버전 상세 문서](kafka_message_processor/README.md)
- [Java Kafka 버전 상세 문서](java_kafka_processor/README.md)
- [Java Kafka 아키텍처 문서](java_kafka_processor/process.md)


