import json
from typing import List, Literal

import pydantic
from bs4 import BeautifulSoup

from coles_vs_woolies.search.session import new_session

_session = new_session()
_session.cookies.update({
    # 'MK_iplz': 'Dqx....GLx',
    # 'MK_iplz-ssn': '02D...GLx',
})


class Product(pydantic.BaseModel):
    class P1(pydantic.BaseModel):
        o: str  # $ value "5.5"

    class A(pydantic.BaseModel):
        A4: str  # ["1.0"]
        O3: str  # weight ["160g"]
        L2: str  # ["false"]
        P8: str  # ["Pantry"]
        W1: str  # ["false"]
        E1: str  # ["false"]
        T1: str  # ["false"]
        T2: str  # ["Chocolate Blocks"]

    p: str  # "9901058P" product code
    p1: P1
    a: A
    s: str  # "cadbury-bubbly-mint-block"
    t: str  # "/wcsstore/Coles-CAS/images/9/9/0/9901058-th.jpg"
    u: str  # "101245"
    s9: str  # "158950"
    pl: str  # "24"
    m: str  # "Cadbury"
    u2: str  # "$3.44 per 100G"
    n: str  # "Dairy Milk Bubbly Mint Milk Chocolate Block"


class ProductPageSearchResult(pydantic.BaseModel):
    type: Literal["COLRSCatalogEntryList"]
    products: List[Product]


def search_coles(search_term: str):
    url = 'https://shop.coles.com.au/online/COLRSSearchDisplay'
    params = {
        'storeId': 20525,
        'catalogId': 29102,
        'searchTerm': search_term,
        'categoryId': None,
        'tabType': 'everything',
        'tabId': 'everything',
        'personaliseSort': False,
        'langId': -1,
        'beginIndex': 0,
        'browseView': False,
        'facetLimit': 100,
        'searchSource': 'Q',
        'sType': 'SimpleSearch',
        'resultCatEntryType': 2,
        'showResultsPage': True,
        'pageView': 'image',
        'errorView': 'AjaxActionErrorResponse',
        'requesttype': 'ajax',
    }
    response = _session.get(url=url, params=params)
    soup = BeautifulSoup(response.text)
    divs = soup.find_all('div', {'data-colrs-transformer': "colrsExpandFilter"})
    good_div = divs[-1]
    the_actually_search_result = json.loads(good_div.text)
    return ProductPageSearchResult.parse_obj(the_actually_search_result)


if __name__ == '__main__':
    search_coles('cadbury')
