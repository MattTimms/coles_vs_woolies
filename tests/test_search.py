import unittest

from coles_vs_woolies.main import get_product_offers
from coles_vs_woolies.search import coles, woolies
from coles_vs_woolies.search.types import Product


class TestSearch(unittest.TestCase):
    # Until society collapses, they should always stock this product
    safe_bet_product = "Cadbury Dairy Milk Chocolate Block 180g"
    non_existent_product = "asdf"  # I tried others but they got false positives

    def test_merchant_search(self):
        product_search_term = self.safe_bet_product
        for merchant in [coles, woolies]:
            product = next(merchant.im_feeling_lucky(product_search_term))
            self.assertIsNotNone(product)
            self.assertIsInstance(product, Product)

    def test_missing_product(self):
        with self.assertRaises(ValueError) as context:
            get_product_offers(product_names=[self.non_existent_product])
        self.assertTrue("No products could be found" in context.exception.args)

    def test_no_products_found(self):
        products = get_product_offers(product_names=[self.non_existent_product, self.safe_bet_product])
        self.assertEqual(len(products), 1)


if __name__ == '__main__':
    unittest.main()
