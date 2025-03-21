import time
import traceback

import requests
from requests import RequestException

from src.config import Config, logger
from src.services.interfaces.token_interface import ITokenService


class HubSpotTokenService(ITokenService):
    def __init__(self):
        self.client_id = Config.HUBSPOT_CLIENT_ID
        self.client_secret = Config.HUBSPOT_CLIENT_SECRET
        self.refresh_token = Config.HUBSPOT_REFRESH_TOKEN
        self.base_url = Config.HUBSPOT_API_BASE

        self.access_token = None
        self.expires_at = 0

    def get_access_token(self):
        # Ideally use a cache (redis) to store the access token for a limited period rather that in memory
        current_time = time.time()
        if self.access_token is None or current_time >= self.expires_at:
            self.refresh_access_token()
        return self.access_token

    def refresh_access_token(self):
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_url = "%s/oauth/v1/token" % self.base_url
        try:
            response = requests.post(token_url, data=payload, headers=headers)
            data = response.json()
            self.access_token = data["access_token"]
            expires_in = data.get("expires_in", 1800)
            self.expires_at = (
                time.time() + expires_in - 60
            )  # Refresh 1 min before expiry
        except (RequestException, ValueError) as e:
            logger.error(
                "Error generating access token",
                context={"error": e, "trace": traceback.format_exc()},
            )
        else:
            logger.info(
                "[TokenService] Access token refreshed successfully.",
            )
