import urllib.parse
from typing import Any, Optional, List, Generator

from pydantic import BaseModel, Extra

from coles_vs_woolies.search import types
from coles_vs_woolies.search.session import new_session


def _woolies_session():
    session = new_session()
    session.get(url='https://www.woolworths.com.au')
    return session


_session = _woolies_session()


class Product(types.Product, BaseModel, extra=Extra.allow):
    merchant = 'woolies'

    TileID: int  # 1
    Stockcode: int  # 153266
    Barcode: Optional[str]  # "9300617296027"
    GtinFormat: int  # 13
    CupPrice: Optional[float]  # 1.67
    InstoreCupPrice: Optional[float]  # 1.67
    CupMeasure: str  # "100G"
    CupString: str  # "$1.67 / 100G"
    InstoreCupString: str  # "$1.67 / 100G"
    HasCupPrice: bool  # true
    InstoreHasCupPrice: bool  # true
    Price: Optional[float]  # None if `IsAvailable=False`
    InstorePrice: Optional[float]  # 6 if `IsAvailable=False`
    Name: str  # "Cadbury Dairy Milk Chocolate Block"
    DisplayName: str  # "Cadbury Dairy Milk Chocolate Block 360g"
    UrlFriendlyName: str  # "cadbury-dairy-milk-chocolate-block"
    Description: str  # " Cadbury Dairy Milk Chocolate<br>Block  360G"
    SmallImageFile: str  # "https://cdn0.woolworths.media/content/wowproductimages/small/153266.jpg"
    MediumImageFile: str  # "https://cdn0.woolworths.media/content/wowproductimages/medium/153266.jpg"
    LargeImageFile: str  # "https://cdn0.woolworths.media/content/wowproductimages/large/153266.jpg"
    IsNew: bool  # false
    IsHalfPrice: bool  # false
    IsOnlineOnly: bool  # false
    IsOnSpecial: bool  # false
    InstoreIsOnSpecial: bool  # false
    IsEdrSpecial: bool  # false
    SavingsAmount: Optional[float]  # 0
    InstoreSavingsAmount: Optional[float]  # 0
    WasPrice: float  # 6
    InstoreWasPrice: float  # 6
    QuantityInTrolley: int  # 0
    Unit: str  # "Each"
    MinimumQuantity: int  # 1
    HasBeenBoughtBefore: bool  # false
    IsInTrolley: bool  # false
    Source: str  # "SearchServiceSearchProducts"
    SupplyLimit: int  # 36
    ProductLimit: int  # 36
    MaxSupplyLimitMessage: str  # "36 item limit"
    IsRanged: bool  # true
    IsInStock: bool  # true
    PackageSize: str  # "360G"
    IsPmDelivery: bool  # false
    IsForCollection: bool  # true
    IsForDelivery: bool  # true
    IsForExpress: bool  # true
    ProductRestrictionMessage: Optional[str]  # null
    ProductWarningMessage: Optional[str]  # null
    UnitWeightInGrams: int  # 0
    SupplyLimitMessage: str  # "'Cadbury Dairy Milk Chocolate Block' has a supply limit of 36. [...]'"
    SmallFormatDescription: str  # "Cadbury Dairy Milk Chocolate Block "
    FullDescription: str  # "Cadbury Dairy Milk Chocolate Block "
    IsAvailable: bool  # true
    InstoreIsAvailable: bool  # false
    IsPurchasable: bool  # true
    InstoreIsPurchasable: bool  # false
    AgeRestricted: bool  # false
    DisplayQuantity: int  # 1
    RichDescription: Optional[str]  # null
    IsDeliveryPass: bool  # false
    HideWasSavedPrice: bool  # false
    Brand: str  # "Cadbury"
    IsRestrictedByDeliveryMethod: bool  # false
    Diagnostics: str  # "0"
    IsBundle: bool  # false
    IsInFamily: bool  # false
    ChildProducts: Any  # null
    UrlOverride: Optional[str]  # null

    def __str__(self):
        price_str = f"unavailable (was ${self.InstoreWasPrice})"
        if self.IsAvailable:
            price_str = f'${self.Price}'
            if self.IsOnSpecial:
                price_str += f' (save ${self.WasPrice - self.Price})'
        return f"{self.DisplayName} | {price_str}"

    @property
    def display_name(self) -> str:
        return self.DisplayName

    @property
    def price(self) -> Optional[float]:
        return self.Price if self.IsAvailable else None

    @property
    def link(self) -> str:
        return f'https://www.woolworths.com.au/shop/productdetails/{self.Stockcode}/{self.UrlFriendlyName}'

    @classmethod
    def fetch_product(cls, product_id: str):
        url = f'https://www.woolworths.com.au/api/v3/ui/schemaorg/product/{product_id}'
        response = _session.get(url=url)
        return Product.parse_obj(response.json())


class ProductSearchResult(BaseModel, extra=Extra.allow):
    Products: Optional[List[Product]]
    Name: str
    DisplayName: str


class ProductPageSearchResult(BaseModel, extra=Extra.allow):
    Products: Optional[List[ProductSearchResult]]
    SearchResultsCount: int
    Corrections: Optional[Any]
    SuggestedTerm: Optional[Any]


def im_feeling_lucky(search_term: str) -> Generator[Product, None, None]:
    paginated_search = search(search_term)
    for page in paginated_search:
        for product in page.Products:
            for _product in product.Products:
                yield _product


def search(search_term: str, page=1) -> Generator[ProductPageSearchResult, None, None]:
    url = 'https://www.woolworths.com.au/apis/ui/Search/products'
    body = {
        'Filters': [],
        'IsSpecial': False,
        'Location': f'/shop/search/products?{urllib.parse.urlencode({"searchTerm": search_term})}',
        'PageNumber': page,
        'PageSize': 36,
        'SearchTerm': search_term,
        'SortType': "TraderRelevance"
    }
    while True:
        response = _session.post(
            url=url,
            # cookies={'bm_sz': _session.cookies.get('bm_sz')},
            json=body,
        ).json()
        search_page = ProductPageSearchResult.parse_obj(response)
        if search_page.Products is None:
            break
        yield search_page
        body['PageNumber'] += 1


if __name__ == '__main__':
    gen = search('Cadbury Dairy Milk Chocolate Block 180g')
    print(next(gen))
