import os

class Config:
    # MongoDB Configuration
    MONGODB_URI = os.environ.get('DOCDB_URI')
    MONGODB_TLS_PATH = os.environ.get('TLSCA_path')
    
    # RabbitMQ Configuration
    RABBITMQ_URI = os.environ.get('AMQPS_URI')
    
    # Logging Configuration
    LOG_DIRS = {
        'ble': '/home/ubuntu/log/BLE',
        'ble_error': '/home/ubuntu/log/BLE_ERROR',
        'lte': '/home/ubuntu/log/LTE',
        'lte_error': '/home/ubuntu/log/LTE_ERROR',
        'nonesub': '/home/ubuntu/log/Nonesub',
        'nonesub_error': '/home/ubuntu/log/Nonesub_ERROR'
    }
    
    @staticmethod
    def ensure_log_dirs():
        """Ensure all log directories exist"""
        for dir_path in Config.LOG_DIRS.values():
            os.makedirs(dir_path, exist_ok=True)