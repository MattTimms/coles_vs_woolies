import json
import pathlib
from unittest.mock import Mock

import pytest

from coles_vs_woolies import merchants

# Dynamically load merchant search response test fixtures
_dir_fixtures = pathlib.Path(__file__).parent / "fixtures"
_mock_keywords_n_path: list[tuple[str, pathlib.Path]] = [
    (str(fp.name).replace("-", " ").replace("_", "."), fp) for fp in _dir_fixtures.iterdir() if fp.is_dir()
]


@pytest.mark.parametrize("keyword", _mock_keywords_n_path, ids=[keyword for keyword, _ in _mock_keywords_n_path])
@pytest.mark.parametrize("merchant", merchants.Merchants, ids=merchants.merchant_names)
def test_each_merchants_search(merchant, keyword):
    # Load merchant search respond fixture
    keyword, dir_ = keyword
    with open(dir_ / f"{merchant.name}.json", "r") as f:
        mock_response = json.load(f)

    # Mock merchant search method
    _search_original = merchant._search
    merchant._search = Mock(side_effect=lambda *args, **kwargs: mock_response)
    session = Mock()

    # Test merchant search
    paged_results = merchant.search(session, keyword)
    assert len(paged_results.products)
