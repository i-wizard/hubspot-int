from abc import ABC, abstractmethod


class ITokenService(ABC):
    @abstractmethod
    def get_access_token(self) -> str:
        pass

    @abstractmethod
    def refresh_access_token(self) -> None:
        pass
