import logging

from src.clients.interfaces.logger import LoggerInterface


class ConsoleLogger(LoggerInterface):
    def __init__(self):
        self.logger = logging.getLogger("custom_logger")
        self.ch = logging.StreamHandler()
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(context)s"
        )
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)
        self.logger.setLevel(logging.INFO)

    # TODO: add a function to remove sensitive params(keys, passwords) before logging

    def info(self, message: str, context: dict = None):
        context = context or {}
        self.logger.info(message, extra={"context": context})

    def error(self, message: str, context: dict = None):
        context = context or {}
        self.logger.error(message, extra={"context": context})