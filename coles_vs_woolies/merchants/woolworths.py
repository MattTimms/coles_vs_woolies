import logging
import urllib.parse
from typing import Any

from pydantic import model_validator
from requests_cache import CachedSession

from . import base

_logger = logging.getLogger(__name__)

NAME: base.MerchantName = "woolworths"


class Product(base.Product):
    merchant: base.MerchantName = NAME

    @model_validator(mode="before")
    def _preprocess(cls, values: dict[str, Any]):
        # Get metadata for determining offer type; e.g. member, standard pricing
        centre_tag = values["CentreTag"]
        is_member_offer = values["ImageTag"]["FallbackText"] == "Member Price"

        # Get product price, price-per-unit, and metadata
        label = None
        # Members pricing
        if is_member_offer and (pd := centre_tag["MemberPriceData"]):
            price = pd["PromotionalPrice"]
            price_per_unit = f"{pd['ComparativeUnitPrice']} per {pd['ComparativeSize']}{pd['ComparativeSizeUom']}"
            label, is_on_special = values["ImageTag"]["FallbackText"], True
        # Members multi-buy
        elif is_member_offer and (pd := centre_tag["MultibuyData"]):
            price = round(pd["Price"] / pd["Quantity"], 2)
            price_per_unit = pd["CupTag"].replace("/", " per ")
            label, is_on_special = centre_tag["TagContentText"], True
        # Standard pricing
        else:
            price = values["Price"] if values["IsAvailable"] else None
            if not (price_per_unit := values["CupString"]):
                price_per_unit = f"{price} per {values['PackageSize']})" if price else None

            # Discount description
            if is_on_special := values["IsOnSpecial"]:
                # "'On Special' 'Save $0.70'"
                label = f"{values['ImageTag']['FallbackText']} {values['HeaderTag']['Content']}"

        # Ensure consistent price-per-unit format
        if price_per_unit is not None:
            price_per_unit = price_per_unit.replace(" / ", " per ").lower()

        # TODO out-of-stock products are ignored; they are detected via NextAvailabilityDate IsInStock

        values.update(
            dict(
                raw=values.copy(),
                display_name=values["DisplayName"],
                price=price,
                size=values["PackageSize"],
                price_per_unit=price_per_unit,
                is_on_special=is_on_special,
                label=label,
                url=f'https://www.woolworths.com.au/shop/productdetails/{values["Stockcode"]}/{values["UrlFriendlyName"]}',
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
            for products in raw.pop("Products") or []  # may be defined as in dict as None
            if (product := products["Products"][0]).get("ThirdPartyProductInfo") is None
        ]


class Woolworths(base.Merchant):
    name: base.MerchantName = NAME
    _search_page_class = SearchResultPage

    _session_id: int = 0

    @staticmethod
    def _search(session: CachedSession, keyword: str, page: int = 1, category: str | None = None):
        # Initialise client
        if Woolworths._session_id != id(session):
            session.get(url="https://www.woolworths.com.au", refresh=True)
            Woolworths._session_id = id(session)

        # Filter query by product category
        _filter = []
        if category == "Fruit & vegetables":
            _filter = [{"Key": "Category", "Items": [{"Term": "1-E5BEE36E"}]}]  # "Fruit & Veg"
        elif category is not None:
            _logger.warning(f"Unsupported category: {category}")

        # Query merchant
        url = "https://www.woolworths.com.au/apis/ui/Search/products"
        body = {
            "Filters": _filter,
            "IsSpecial": False,
            "Location": f'/shop/search/products?{urllib.parse.urlencode({"searchTerm": keyword})}',
            "PageNumber": page,
            "PageSize": 36,
            "SearchTerm": keyword,
            "SortType": "TraderRelevance",
        }
        response = session.post(url=url, json=body)
        if not response.from_cache:
            _logger.debug(f"cache='miss' {keyword=} merchant={Woolworths.name}")
        return response.json()
