import os
import ssl

import requests
from dotenv import load_dotenv, find_dotenv
from requests import PreparedRequest, Response
from requests.adapters import HTTPAdapter

load_dotenv(dotenv_path=find_dotenv())

ssl._create_default_https_context = ssl._create_unverified_context  # noqa
TOKEN = os.getenv("SCRAPERBOX_TOKEN")


class ScraperBoxProxyAdapter(HTTPAdapter):
    url = "https://api.scraperbox.com/scrape"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send(self, request: PreparedRequest, **kwargs) -> Response:
        if request.method == 'GET':
            new_request = requests.Request(
                method='GET',
                url=self.url,
                params={
                    'token': TOKEN,
                    'url': request.url,
                    'proxy_location': "au",
                    'residential_proxy': True
                }
            )
        elif request.method == 'POST':
            new_request = requests.Request(
                method='POST',
                url=self.url,
                params={
                    'token': TOKEN,
                    'url': request.url,
                    'post_body': request.body,
                    'proxy_location': "au",
                    'residential_proxy': True
                },
                headers={'SB-Content-Type': 'application/json'}
            )
        else:
            raise ValueError("unsupported request method for scraperbox proxy")
        return super().send(new_request.prepare(), **kwargs)
