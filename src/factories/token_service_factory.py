from src.services.interfaces.token_interface import ITokenService
from src.services.token_service import HubSpotTokenService


class TokenServiceFactory:
    _providers = {}

    @classmethod
    def register_provider(cls, name: str, provider_cls):
        cls._providers[name] = provider_cls

    @classmethod
    def get_provider(cls, name: str, **kwargs) -> ITokenService:
        if name not in cls._providers:
            raise ValueError(f"Unknown logger provider: {name}")
        return cls._providers[name](**kwargs)


TokenServiceFactory.register_provider("hubspot", lambda: HubSpotTokenService())
