import abc
import logging
from typing import Any, Iterable, Literal, Type, TypeVar

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, computed_field, constr
from requests_cache import CachedSession
from typing_extensions import Annotated

from ..utils.similarity import jaccard_similarity

_logger = logging.getLogger(__name__)

MerchantName = Literal["coles", "woolworths", "iga"]


class Product(BaseModel):  # abc.ABC
    model_config = ConfigDict(coerce_numbers_to_str=True)

    keyword: str
    merchant: MerchantName

    index: int
    display_name: str  # incl. brand & size; e.g. 'Cadbury Dairy Milk Chocolate Block 180g'
    price: str | None  # string numeric e.g. '1.23'
    size: constr(to_lower=True) | None
    price_per_unit: str | None  # e.g. '$4.29 per 100g'
    is_on_special: bool
    label: str | None  # discount labelling, e.g. '20% Off save $1.40'
    url: AnyHttpUrl

    raw: dict[str, Any] = Field(exclude=True)

    @computed_field
    @property
    def similarity_score(self) -> float:
        return round(jaccard_similarity(self.keyword, self.display_name), 2)

    def __lt__(self, other: "Product"):
        # n.b. all that's required for sorted()/.sort()
        # default to big number when no price available
        return float((self.price or 1e6)) < float((other.price or 1e6))

    def __str__(self):
        price = self.price or "n/a"
        price_per_unit = self.price_per_unit or "n/a"
        label = self.label or "standard price"
        return f"{self.display_name} | ${price} | {price_per_unit} | {label}"


ProductClass = TypeVar("ProductClass", bound=Product)


class SearchResultPage(BaseModel, abc.ABC):
    merchant: MerchantName
    _product_class: Type[ProductClass]

    keyword: str
    products: list[Annotated[ProductClass, "Merchant's product class"]]
    raw: dict[str, Any]  # API response without products

    def __iter__(self) -> Iterable[ProductClass]:
        return iter(self.products)

    def __len__(self):
        return len(self.products)

    @staticmethod
    @abc.abstractmethod
    def preprocess_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
        """Preform any required preprocessing of API response to return list of product dictionaries."""
        pass

    @classmethod
    def from_response(cls, raw: dict[str, Any], keyword: str, page_idx: int = 0):  # TODO support multi-page
        products = []
        results = cls.preprocess_response(raw)
        for i, result in enumerate(results):
            try:
                product_class = cls._product_class.get_default()
                products.append(product_class(**result, keyword=keyword, index=page_idx + i))
            except (TypeError, Exception):
                _logger.warning(f"ignoring product, could not parse: {result}", exc_info=True)
                continue
        return cls(keyword=keyword, products=products, raw=raw)

    def best_match(self) -> "ProductClass":
        return max(self.products, key=lambda product: product.similarity_score)

    def display(self):
        """Prints product result page to console."""
        from ..utils import display

        title = f"{self.merchant.upper()}: {self.keyword}"
        display.product_table(title, products=self.products)


SearchResultPageClass = TypeVar("SearchResultPageClass", bound=SearchResultPage)


class Merchant(abc.ABC):
    name: MerchantName
    _search_page_class: SearchResultPageClass

    def search(
        self, session: CachedSession, keyword: str, page: int = 1, category: str | None = None
    ) -> SearchResultPageClass:
        if category is not None:
            _logger.warning("Category support is WIP")
        response = self._search(session, keyword, page, category)
        search_page = self._search_page_class.from_response(response.copy(), keyword)
        return search_page

    @staticmethod
    @abc.abstractmethod
    def _search(session: CachedSession, keyword: str, page: int = 1, category: str | None = None) -> dict[str, Any]:
        pass


MerchantClass = TypeVar("MerchantClass", bound=Merchant)
