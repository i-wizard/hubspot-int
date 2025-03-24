from abc import ABC, abstractmethod
from typing import Optional, Any


class ICacheClient(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 0) -> None:
        pass
