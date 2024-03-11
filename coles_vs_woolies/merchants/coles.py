import json
import logging
import urllib.parse
from typing import Any, Optional

from bs4 import BeautifulSoup
from pydantic import model_validator
from requests_cache import CachedSession

from . import base

_logger = logging.getLogger(__name__)

NAME: base.MerchantName = "coles"


class Product(base.Product):
    merchant: base.MerchantName = NAME

    @model_validator(mode="before")
    def _preprocess(cls, values: dict[str, Any]):
        size = values["size"]
        pricing: dict = values.get("pricing") or {}  # value may be None
        display_name = f"{values['brand']} {values['name'].rstrip()} {size}".replace("\xa0", "")
        price_per_unit = pricing.get("comparable")  # "$##.## per ##kg"

        # Discount description label
        label = None
        if pricing.get("promotionType") == "SPECIAL":
            if (special_type := values.get("specialType")) is None:
                label = pricing.get("saveStatement")  # 'save $#.##'
            elif special_type == "MULTI_SAVE":
                label = values.get("offerDescription")  # 'Pick any 2 for $#.##'
            elif special_type == "PERCENT_OFF":
                label = values.get("priceDescription")  # '1/2 Price'
            else:
                _logger.warning(f"unsupported promotion type: {special_type}")
                label = pricing.get("saveStatement")

        values.update(
            dict(
                raw=values.copy(),
                display_name=display_name,
                price=pricing.get("now"),
                size=size,
                price_per_unit=price_per_unit,
                is_on_special="saveAmount" in pricing,
                label=label,
                url=f'https://www.coles.com.au/product/{display_name.replace(" ", "-")}-{values["id"]}',
            )
        )
        return values


class SearchResultPage(base.SearchResultPage):
    merchant: base.MerchantName = NAME
    products: list[Product]
    _product_class = Product

    @staticmethod
    def preprocess_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            product
            for product in raw.pop("results", [])
            # filter if not product entry; e.g. ad, product suggestion
            if product.get("_type") == "PRODUCT"
        ]


class Coles(base.Merchant):
    name: base.MerchantName = NAME
    _search_page_class = SearchResultPage

    _api_build_id: Optional[str] = None

    @staticmethod
    def init_api(session: CachedSession):
        """Retrieve Coles' API build ID"""
        url = "https://www.coles.com.au/"
        response = session.get(url=url, refresh=True)  # Must be fresh, build updates constantly
        soup = BeautifulSoup(response.text, features="html.parser")
        api_data = json.loads(str(soup.find(id="__NEXT_DATA__").contents[0]))
        Coles._api_build_id = api_data["buildId"]  # e.g. 20221208.01_v3.19.0

    @staticmethod
    def _search(session: CachedSession, keyword: str, page: int = 1, category: str | None = None):
        # Initialise client
        if Coles._api_build_id is None:
            Coles.init_api(session)

        # Filter query by product category
        _category = {}
        if category == "Fruit & vegetables":
            _category = dict(categoryName=urllib.parse.quote_plus(category), categoryId="2100", categoryLevel="1")
        elif category is not None:
            _logger.warning(f"Unsupported category: {category}")

        # Query merchant
        url = f"https://www.coles.com.au/_next/data/{Coles._api_build_id}/en/search.json"
        response = session.get(url=url, params={"q": keyword, "page": page, **_category})
        if not response.from_cache:
            _logger.debug(f"cache='miss' {keyword=} merchant={Coles.name}")
        return response.json()["pageProps"]["searchResults"]
