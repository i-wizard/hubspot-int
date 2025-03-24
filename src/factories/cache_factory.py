from src.clients.interfaces.cache import ICacheClient
from src.clients.redis import RedisCacheClient


class CacheFactory:
    _providers = {}

    @classmethod
    def register_provider(cls, name: str, provider_cls):
        cls._providers[name] = provider_cls

    @classmethod
    def get_provider(cls, name: str, **kwargs) -> ICacheClient:
        if name not in cls._providers:
            raise ValueError(f"Unknown cache provider: {name}")
        return cls._providers[name](**kwargs)


CacheFactory.register_provider("redis", lambda: RedisCacheClient())
