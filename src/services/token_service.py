import traceback

import requests
from requests import RequestException

from src.config import Config, logger
from src.factories.cache_factory import CacheFactory
from src.services.interfaces.token_interface import ITokenService


class HubSpotTokenService(ITokenService):
    CACHE_KEY = "hubspot_access_token"

    def __init__(self):
        self.client_id = Config.HUBSPOT_CLIENT_ID
        self.client_secret = Config.HUBSPOT_CLIENT_SECRET
        self.refresh_token = Config.HUBSPOT_REFRESH_TOKEN
        self.base_url = Config.HUBSPOT_API_BASE

        self.cache = CacheFactory.get_provider(Config.CACHE_CLIENT)

    def get_access_token(self):
        token_data = self.cache.get(self.CACHE_KEY)
        if token_data:
            return token_data.get("access_token")

        token_data = self.refresh_access_token()
        return token_data.get("access_token") if token_data else None

    def refresh_access_token(self):
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_url = f"{self.base_url}/oauth/v1/token"
        try:
            response = requests.post(token_url, data=payload, headers=headers)
            data = response.json()
            access_token = data["access_token"]
            expires_in = data.get("expires_in", 1800)

            # Cache the token with a TTL slightly shorter than expiry
            self.cache.set(
                self.CACHE_KEY,
                {"access_token": access_token},
                ttl=expires_in - 60,
            )

        except (RequestException, ValueError) as e:
            logger.error(
                "Error refreshing access token",
                context={"error": str(e), "trace": traceback.format_exc()},
            )
            return None
        else:
            logger.info("[TokenService] Access token refreshed and cached.")
            return {"access_token": access_token}
