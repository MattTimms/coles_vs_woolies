import json
from typing import List, Literal, Optional, Generator

from bs4 import BeautifulSoup
from pydantic import BaseModel, Extra

from coles_vs_woolies.search import types
from coles_vs_woolies.search.session import new_session

_session = new_session()


def _init() -> str:
    url = 'https://www.coles.com.au/'
    response = _session.get(url=url)
    soup = BeautifulSoup(response.text, features="html.parser")
    api_data = json.loads(soup.find(id='__NEXT_DATA__').contents[0])
    build_id = api_data['buildId']  # 20221208.01_v3.19.0
    return build_id


_BUILD_ID = _init()


class Product(types.Product, BaseModel, extra=Extra.allow):
    merchant = 'coles'

    class Pricing(BaseModel, extra=Extra.allow):
        class Unit(BaseModel, extra=Extra.allow):
            quantity: int  # 1
            ofMeasureQuantity: Optional[int]  # 100
            ofMeasureUnits: Optional[str]  # "g"
            price: Optional[float]  # 2
            ofMeasureType: Optional[str]  # "g"
            isWeighted: bool = False  # false

        now: float  # 6
        was: float  # 6.5
        saveAmount: Optional[float]  # 0.5
        priceDescription: Optional[str]  # "Was $6.50 on Sep 2022"
        savePercent: Optional[float]  # 50
        saveStatement: Optional[str]  # "save $5.00"
        unit: Unit

        comparable: str  # "$2.00 per 100g"
        promotionType: Optional[str]  # "DOWNDOWN", "SPECIAL"
        specialType: Optional[str]  # "PERCENT_OFF", "MULTI_SAVE", "WHILE_STOCKS_LAST"
        onlineSpecial: bool  # false

    _type: Literal['PRODUCT']
    id: int  # 2351888
    name: str  # "Cadbury Clinkers Lollies"
    brand: str  # "Pascall"
    description: str  # "PASCALL CADBURY CLINKERS 300G"
    size: str  # "300g"
    availability: bool  # true
    availabilityType: str  # "InStoreAndOnline"
    pricing: Optional[Pricing]  # None if `availability=False`

    def __str__(self):
        price_str = f"unavailable ${self.pricing.now}"
        if self.availability:
            price_str = f'${self.pricing.now}'
            if self.pricing.saveStatement:
                price_str += f' ({self.pricing.saveStatement})'
        return f"{self.brand} {self.name} {self.size} | {price_str}"

    @property
    def display_name(self) -> str:
        return f"{self.brand} {self.name} {self.size}"

    @property
    def price(self) -> Optional[float]:
        return self.pricing.now if self.availability else None

    @property
    def is_on_special(self) -> Optional[bool]:
        return self.pricing.saveAmount is not None

    @property
    def link(self) -> str:
        return f'https://www.coles.com.au/product/{self.display_name.replace(" ", "-")}-{self.id}'


class ProductPageSearchResult(BaseModel, extra=Extra.allow):
    start: int  # 0
    didYouMean: Optional[list]  # null
    noOfResults: int  # 182
    start: int  # 0
    pageSize: int  # 48
    keyword: str  # "cadbury chocolate"
    resultType: int  # 1
    results: List[Product]

    def search_exact(self, product_name: str) -> Optional[Product]:
        """ Return product that matches product_name within list of paged results """
        for product in self.results:
            if product.name == product_name:
                return product
        else:
            return None


def im_feeling_lucky(search_term: str) -> Generator[Product, None, None]:
    paginated_search = search(search_term)
    for page in paginated_search:
        for product in page.results:
            yield product


def search(search_term: str, specials_only: bool = False) -> Generator[ProductPageSearchResult, None, None]:
    url = f'https://www.coles.com.au/_next/data/{_BUILD_ID}/en/search.json'
    params = {
        'q': search_term,
        'page': 1,
    }
    if specials_only:
        params['filter_Special'] = 'all'

    while True:
        response = _session.get(url=url, params=params).json()
        search_page = ProductPageSearchResult.parse_obj(response['pageProps']['searchResults'])
        if search_page.noOfResults == 0:
            break
        yield search_page
        params['page'] += 1


if __name__ == '__main__':
    gen = search('Cadbury Dairy Milk Chocolate Block 180g')
    print(next(gen))
