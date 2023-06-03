from typing import Any, Optional, List, Generator, Dict

from pydantic import BaseModel, Extra

from coles_vs_woolies.search import types
from coles_vs_woolies.search.session import new_session
from coles_vs_woolies.search.similarity import jaccard_similarity

_session = new_session()
_DEFAULT_STORE = 52511  # SUPA IGA Georges Hall


class Product(types.Product, BaseModel, extra=Extra.allow):
    merchant = 'iga'

    class Size(BaseModel, extra=Extra.allow):
        abbreviation: str  # "ml"
        label: str  # "Millilitre"
        size: int  # 500
        type: str  # "millilitre"

        def __str__(self):
            return f"{self.size}{self.abbreviation}"

    # attributes: ...
    available: bool
    barcode: str
    brand: str
    # categories: ...
    # defaultCategory: ...
    description: str
    image: dict[str, str]
    isFavorite: bool
    isPastPurchased: bool
    name: str
    # price: str  # "$3.20" n.b. omitted due to clash with class-property
    priceLabel: str
    priceNumeric: float  # 3.2
    pricePerUnit: str  # "$0.64/100ml"
    priceSource: str
    productId: str
    sellBy: str
    sku: str
    # tprPrice: ...
    # unitOfMeasure: ...
    # unitOfPrice: ...
    unitOfSize: Size
    wasPrice: Optional[str]
    wasPriceNumeric: Optional[float]
    wasWholePrice: Optional[float]
    weightIncrement: Any
    wholePrice: float

    def __str__(self):
        price_str = f'${self.price}'
        if self.wasPrice is not None:
            price_str += f' (save ${self.wasPriceNumeric - self.price:.2f})'
        return f"{self.display_name} | {price_str}"

    @property
    def display_name(self) -> str:
        return f"{self.name} {self.unitOfSize}"

    @property
    def price(self) -> Optional[float]:
        return self.priceNumeric

    @property
    def is_on_special(self) -> Optional[bool]:
        return self.priceLabel != ""

    @property
    def link(self) -> str:
        product_slug = "-".join(self.name.lower().split()) + '-' + self.productId
        return f'https://www.igashop.com.au/product/{product_slug}'

    @classmethod
    def fetch_product(cls, product_id: str, store_id: int = _DEFAULT_STORE):
        url = f"https://www.igashop.com.au/api/storefront/stores/{store_id}/products/{product_id}"
        response = _session.get(url=url)
        return Product.parse_obj(response.json())


class ProductPageSearchResult(BaseModel, extra=Extra.allow):
    count: int  # page count
    items: list[Product]
    total: int  # total results


def im_feeling_lucky(search_term: str) -> Generator[Product, None, None]:
    paginated_search = search(search_term)
    for page in paginated_search:
        page.items.sort(key=lambda x: jaccard_similarity(search_term, x.display_name), reverse=True)
        for product in page.items:
            yield product


def search(search_term: str) -> Generator[ProductPageSearchResult, None, None]:
    url = f'https://www.igashop.com.au/api/storefront/stores/{_DEFAULT_STORE}/search'
    params = {
        'q': search_term[:50],  # n.b. no results if query > 50
        'skip': 0,
        'take': 40
    }
    while True:
        response = _session.get(url=url, params=params).json()
        search_page = ProductPageSearchResult.parse_obj(response)
        if len(search_page.items) == 0:
            break
        yield search_page
        params['skip'] += params['take']


if __name__ == '__main__':
    gen = search('Cadbury Dairy Milk Chocolate Block 180g')
    print(next(gen))
