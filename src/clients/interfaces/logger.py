from abc import ABC, abstractmethod


class LoggerInterface(ABC):
    @abstractmethod
    def info(self, message: str, context: dict = None):
        pass

    @abstractmethod
    def error(self, message: str, context: dict = None):
        pass

