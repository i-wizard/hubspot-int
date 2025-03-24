import json
from typing import Optional, Any

import redis

from src.clients.interfaces.cache import ICacheClient
from src.config import Config


class RedisCacheClient(ICacheClient):
    def __init__(self):
        self.client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            decode_responses=True,
        )

    def get(self, key: str) -> Optional[Any]:
        value = self.client.get(key)
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    def set(self, key: str, value: Any, ttl: int = 0) -> None:
        value = json.dumps(value)
        if ttl > 0:
            self.client.setex(key, ttl, value)
        else:
            self.client.set(key, value)
