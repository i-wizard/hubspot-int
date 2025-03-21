import os

from src.factories.logger_factory import LoggerFactory


class Config:
    HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID", "xxxx")
    HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET", "xxxxx")
    HUBSPOT_REFRESH_TOKEN = os.getenv("HUBSPOT_REFRESH_TOKEN", "xxxxx")
    HUBSPOT_API_BASE = "https://api.hubapi.com"
    LOGGER = os.getenv('LOGGER', 'console')
    REPOSITORY = os.getenv("REPOSITORY", "hubspot")
    TOKEN_CLIENT = os.getenv("TOKEN_CLIENT", "hubspot")

class TestConfig(Config):
    TESTING = True


logger = LoggerFactory.get_provider(Config.LOGGER)