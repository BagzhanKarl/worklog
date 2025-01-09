from app.config.base import BaseConfig
from app.config.dev import DevelopmentConfig
from app.config.test import TestingConfig
from app.config.prod import ProductionConfig

config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}