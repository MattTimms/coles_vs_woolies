import logging
from typing import Any

from pydantic import model_validator
from requests_cache import CachedSession

from . import base

_logger = logging.getLogger(__name__)


NAME: base.MerchantName = "iga"


class Product(base.Product):
    merchant: base.MerchantName = NAME

    @model_validator(mode="before")
    @classmethod
    def _preprocess(cls, values: dict[str, Any]):
        # Display name & size
        name = values["name"]
        unit_of_size = values["unitOfSize"]
        size, abbreviation = unit_of_size["size"], unit_of_size["abbreviation"]
        display_size = f"{size}{abbreviation}"
        display_name = f"{name} {display_size}"
        if unit_of_size["type"] == "each":
            if size > 1:
                display_size = f"{size} Pack"
                display_name = f"{name} {display_size}"
            elif not abbreviation:
                display_size = None
                display_name = name

        # Price per unit
        if price_per_unit := values.get("pricePerUnit"):  # "$##.##/##kg"
            price_per_unit = price_per_unit.replace("/", " per ")
        else:
            unit_of_measure = values["unitOfMeasure"]
            if unit_of_measure["label"] == "Each" and unit_of_measure["size"] == 1:
                price_per_unit = values["price"] + " each"

        # Discount description
        label = None
        price = values["priceNumeric"]
        if is_on_special := values["priceLabel"] != "":
            was_price = values["wasPriceNumeric"]  # '36.7'
            label = f"{values['priceLabel']} save ${was_price - price:.2f}"

        product_slug = "-".join(name.lower().replace("'", "").split()) + "-" + values["productId"]
        values.update(
            dict(
                raw=values.copy(),
                display_name=display_name,
                price=price,
                size=display_size,
                price_per_unit=price_per_unit,
                is_on_special=is_on_special,
                label=label,
                url=f"https://www.igashop.com.au/product/{product_slug}",
            )
        )
        return values


class SearchResultPage(base.SearchResultPage):
    merchant: base.MerchantName = NAME
    products: list[Product]
    _product_class = Product

    @staticmethod
    def preprocess_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
        return raw.pop("items", [])


class IGA(base.Merchant):
    name: base.MerchantName = NAME
    _search_page_class = SearchResultPage

    _default_store_id = 52511  # SUPA IGA Georges Hall

    @staticmethod
    def _search(session: CachedSession, keyword: str, page: int = 1, category: str | None = None):
        take = 40
        skip = take * (page - 1)
        url = f"https://www.igashop.com.au/api/storefront/stores/{IGA._default_store_id}/search"

        params = {
            "q": keyword[:50],  # n.b. no results if query > 50
            "skip": skip,
            "take": take,
            "misspelling": "true",
        }
        response = session.get(url=url, params=params)
        if not response.from_cache:
            _logger.debug(f"cache='miss' {keyword=} merchant={IGA.name}")
        return response.json()
