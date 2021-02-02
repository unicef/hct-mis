import os
import time
from io import BytesIO

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from requests.packages.urllib3.util.retry import Retry

from hct_mis_api.apps.core.kobo.common import filter_by_owner
from hct_mis_api.apps.core.models import BusinessArea


class TokenNotProvided(Exception):
    pass


class TokenInvalid(Exception):
    pass


class KoboAPI:
    KPI_URL = os.getenv("KOBO_API_URL", "https://kobo.humanitarianresponse.info")

    def __init__(self, business_area_slug, kpi_url: str = None):
        if kpi_url:
            self.KPI_URL = kpi_url
        self.business_area = BusinessArea.objects.get(slug=business_area_slug)
        self._get_token()

    def _handle_paginated_results(self, url):
        next_url = url
        results: list = []

        # if there will be more than 30000 results,
        # we need to make additional queries
        while next_url:
            data = self._handle_request(next_url)
            next_url = data["next"]
            results.extend(data["results"])
        return results

    def _get_url(self, endpoint: str, append_api=True, add_limit=True):
        endpoint.strip("/")
        if endpoint != "token" and append_api is True:
            endpoint = f"api/v2/{endpoint}"
        # According to the Kobo API documentation,
        # the maximum limit per page is 30000
        return f"{self.KPI_URL}/{endpoint}?format=json{'&limit=30000' if add_limit else ''}"

    def _get_token(self):
        self._client = requests.session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504], method_whitelist=False)
        self._client.mount(self.KPI_URL, HTTPAdapter(max_retries=retries))

        token = settings.KOBO_MASTER_API_TOKEN

        if not token:
            raise TokenNotProvided("Token is not set")

        self._client.headers.update({"Authorization": f"token {token}"})

    def _handle_request(self, url) -> dict:
        response = self._client.get(url=url)
        response.raise_for_status()
        return response.json()

    def _post_request(self, url, data=None, files=None) -> requests.Response:
        response = self._client.post(url=url, data=data, files=files)
        return response

    def _patch_request(self, url, data=None, files=None) -> requests.Response:
        response = self._client.patch(url=url, data=data, files=files)
        return response

    def create_template_from_file(self, bytes_io_file, template_id=""):
        data = {
            "name": "Untitled",
            "asset_type": "template",
            "description": "",
            "sector": "",
            "country": "",
            "share-metadata": False,
        }
        if not template_id:
            asset_response = self._post_request(url=self._get_url("assets/", add_limit=False), data=data)
            asset_response_dict = asset_response.json()
            asset_uid = asset_response_dict.get("uid")
        else:
            asset_uid = template_id
        file_import_data = {
            "assetUid": asset_uid,
            "destination": self._get_url(f"assets/{asset_uid}/", append_api=False, add_limit=False),
        }
        file_import_response = self._post_request(
            url=self._get_url("imports/", append_api=False, add_limit=False),
            data=file_import_data,
            files={"file": bytes_io_file},
        )
        file_import_response_dict = file_import_response.json()
        url = file_import_response_dict.get("url")

        attempts = 5
        while attempts >= 0:
            response_dict = self._handle_request(url)
            import_status = response_dict.get("status")
            if import_status == "processing":
                attempts -= 1
                time.sleep(0.3)
            else:
                return response_dict, asset_uid

        raise RetryError("Fetching import data took too long")

    def get_all_projects_data(self) -> list:
        projects_url = self._get_url("assets")

        response_dict = self._handle_paginated_results(projects_url)
        return filter_by_owner(response_dict, self.business_area)

    def get_single_project_data(self, uid: str) -> dict:
        projects_url = self._get_url(f"assets/{uid}")

        return self._handle_request(projects_url)

    def get_project_submissions(self, uid: str) -> list:
        submissions_url = self._get_url(f"assets/{uid}/data")

        response_dict = self._handle_paginated_results(submissions_url)
        return response_dict

    def get_attached_file(self, url: str) -> BytesIO:
        response = self._client.get(url=url)
        response.raise_for_status()
        file = BytesIO(response.content)
        return file
