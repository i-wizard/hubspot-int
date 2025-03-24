import os

from src.factories.logger_factory import LoggerFactory


class Config:
    HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID", "xxxx")
    HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET", "xxxxx")
    HUBSPOT_REFRESH_TOKEN = os.getenv("HUBSPOT_REFRESH_TOKEN", "xxxxx")
    HUBSPOT_API_BASE = os.getenv("HUBSPOT_BASE_URL", "https://api.hubapi.com")
    LOGGER = os.getenv('LOGGER', 'console')
    REPOSITORY = os.getenv("REPOSITORY", "hubspot")
    TOKEN_CLIENT = os.getenv("TOKEN_CLIENT", "hubspot")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    CACHE_CLIENT = os.getenv("CACHE_CLIENT", "redis")

class TestConfig(Config):
    TESTING = True


logger = LoggerFactory.get_provider(Config.LOGGER)