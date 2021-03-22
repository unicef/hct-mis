import logging

import requests
from django.conf import settings
from django.http import Http404

logger = logging.getLogger(__name__)

DJANGO_USER_MAP = {
    "username": "mail",
    "email": "mail",
    "first_name": "givenName",
    "last_name": "surname",
    "ad_uuid": "id",
}


class MicrosoftGraphAPI:
    def __init__(self):
        self.azure_client_id = settings.AZURE_CLIENT_ID
        self.azure_client_secret = settings.AZURE_CLIENT_SECRET
        self.access_token = self.get_token()

    def get_token(self):
        if not self.azure_client_id or not self.azure_client_secret:
            logger.error("Configure AZURE_CLIENT_ID and/or AZURE_CLIENT_SECRET")
            raise ValueError("Configure AZURE_CLIENT_ID and/or AZURE_CLIENT_SECRET")

        post_dict = {
            "grant_type": "client_credentials",
            "client_id": self.azure_client_id,
            "client_secret": self.azure_client_secret,
            "resource": settings.AZURE_GRAPH_API_BASE_URL,
        }
        response = requests.post(settings.AZURE_TOKEN_URL, post_dict)

        if response.status_code != 200:
            logger.error(f"Unable to fetch token from Azure. {response.status_code} {response.content}")
            raise Exception(f"Error during token retrieval: {response.status_code} {response.content}")

        json_response = response.json()
        token = json_response["access_token"]
        return token

    def get_results(self, url):
        headers = {"Authorization": "Bearer {}".format(self.access_token)}
        response = requests.get(url, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(e)
            raise
        json_response = response.json()
        return json_response

    def get_user_data(self, *, email=None, uuid=None):
        try:
            if uuid:
                q = f"https://graph.microsoft.com/beta/users/{uuid}"
                value = self.get_results(q)
            elif email:
                q = f"https://graph.microsoft.com/beta/users/?$filter=userType in ['Member','guest'] and mail eq '{email}'"
                data = self.get_results(q)
                value = data.get("value")[0]
            else:
                logger.error("You must provide 'uuid' or 'email' argument.")
                raise ValueError("You must provide 'uuid' or 'email' argument.")
        except (IndexError,):
            logger.error(f"User not found using email={email},uuid={uuid}")
            raise Http404("User not found")
        if not value:
            logger.error(f"User not found using email={email},uuid={uuid}")
            raise Http404("User not found")
        return value
