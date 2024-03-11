import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

import pandas as pd
from requests_cache import CachedSession
from typing_extensions import Annotated

from . import merchants
from .utils import display
from .utils.session import new_session

_logger = logging.getLogger(__name__)
_num_workers = len(merchants.Merchants)

MAGIC_SIMILARITY_MIN = 0.4


class Search:
    def __init__(self, keyword: str, session: CachedSession = None):
        self.keyword = keyword
        self._session: CachedSession = session or new_session()

        self.results: list[merchants.SearchResultPage] = []
        with ThreadPoolExecutor(max_workers=_num_workers) as executor:
            futures = [
                executor.submit(merchant.search, session=self._session, keyword=keyword)
                for merchant in merchants.Merchants
            ]
            for future in as_completed(futures):
                paged_result: merchants.SearchResultPage = future.result()
                self.results.append(paged_result)
        self.results.sort(key=lambda x: x.merchant)

    def im_feeling_lucky(self) -> list[merchants.ProductClass]:
        """Return list of best (opinionated) search matches for each merchant if applicable."""
        return [
            product
            for page in self.results
            if page.products and (product := page.best_match()).similarity_score > MAGIC_SIMILARITY_MIN
        ]

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([product.model_dump() for page in self.results for product in page])

    def display(self, isolate_by_merchant: bool = True):
        """Prints product result page to console."""
        if isolate_by_merchant:
            for result in self.results:
                result.display()
        else:
            products = list(product for result in self.results for product in result.products)
            display.product_table(title=self.keyword, products=products)


class BulkSearch:
    def __init__(self, keywords: Iterable[str], session: CachedSession = None):
        self.keywords = keywords
        self._session: CachedSession = session or new_session()

        self.searches_dict: dict[Annotated[str, "keyword"], Search] = {}
        with ThreadPoolExecutor(max_workers=_num_workers) as executor:
            futures = {executor.submit(Search, keyword=keyword, session=self._session): keyword for keyword in keywords}
            for future in as_completed(futures):
                keyword: str = futures[future]
                search_result: Search = future.result()
                self.searches_dict[keyword] = search_result

        # Order results by input keywords
        self.searches: list[Search] = [self.searches_dict[keyword] for keyword in keywords]

    def __iter__(self) -> Iterable[Search]:
        return iter(self.searches)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"keyword": keyword, **product.model_dump()}
                for keyword in self.keywords
                for page in self.searches_dict[keyword].results
                for product in page
            ]
        )

    def display(self, isolate_by_merchant: bool = True):
        """Prints product result page to console."""
        for search in self.searches:
            search.display(isolate_by_merchant=isolate_by_merchant)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    _common_purchases = [  # Really helps to have weight/quantity
        "Cadbury Dairy Milk Chocolate Block 180g",
        "Cadbury Dairy Milk Vanilla Sticks 4 Pack",
        "Connoisseur Ice Cream Vanilla 4 Pack",
        "Connoisseur Ice Cream Vanilla Caramel Brownie 1L",
        "The Juice Brothers 1.5L",
    ]
    responses = BulkSearch(_common_purchases)
    for response in responses:
        response.show_results()
    logger.info("fin")
