from src.config import Config
from src.factories.token_service_factory import TokenServiceFactory
from src.repositories import IRepository
from src.repositories.hubspot_repository import HubSpotRepository


class RepositoryFactory:
    _providers = {}

    @classmethod
    def register_provider(cls, name: str, provider_cls):
        cls._providers[name] = provider_cls

    @classmethod
    def get_provider(cls, name: str, **kwargs) -> IRepository:
        if name not in cls._providers:
            raise ValueError(f"Unknown logger provider: {name}")
        return cls._providers[name](**kwargs)


token_client = TokenServiceFactory.get_provider(Config.TOKEN_CLIENT)
RepositoryFactory.register_provider(
    "hubspot", lambda: HubSpotRepository(token_service=token_client)
)
