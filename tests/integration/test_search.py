"""This smoke test (if you can call it that) runs search for a large list of product keywords."""

from coles_vs_woolies import merchants, search

_original_keywords = [
    "Cadbury Dairy Milk Chocolate Block 180g",
    "Cadbury Dairy Milk Vanilla Sticks 4 Pack",
    "Connoisseur Ice Cream Vanilla 4 Pack",
    "Connoisseur Ice Cream Vanilla Caramel Brownie 1L",
    "The Juice Brothers 1.5L",
]
_special_keywords = [
    "Coconut Cream 400ml",
    "Coconut Milk 400ml 270ml",
    "Coca-Cola Zero Sugar Soft Drink Multipack Cans",
    "Schweppes Zero Sugar Mixers Indian Tonic Water Bottles Multipack",
    "Nutella Hazelnut Spread With Cocoa 1kg",
    "KitKat Milk Chocolate Block 160g",
    "Nutella Hazelnut Chocolate Spread kg",
    "Ayam Paste Thai Massaman Curry",
    "Nutella Hazelnut Chocolate Spread",
    "Old El Paso Reduced Salt Spice Mix Taco",
    "La Famiglia Cheesy Garlic Bread 460g",
    "Coconut Milk 400ml",
    "Laoganma",
    "S&B Golden Curry 92g",
]
_generated_keywords = [
    "Bagels Pack",
    "Black Beans 400g",
    "Black Beans No Added Salt",
    "Brioche Burger Buns",
    "Butter Unsalted" "Chicken Breast Fillets",
    "Chicken Breast Schnitzel RSPCA",
    "Chicken Schnitzel Crumbed Each",
    "Coconut Cream 400mL",
    "Diced Beef",
    "Eggs Pack",
    "Eggs",
    "English Muffin Pack",
    "English Muffins",
    "Garlic Bread",
    "Jasmine Rice kg",
    "Lasagne Sheets",
    "Mascarpone",
    "Mission Strips",
    "Mozzarella Cheese",
    "Naan Pack",
    "Pasta Sauce",
    "Pork Dumplings",
    "Rana Ravioli",
    "Roti",
    "Shortcut Bacon",
    "Sour Cream",
    "Sweet Chilli Chicken Tenders",
    "unsalted butter",
]
_merchant_unique_keywords = [
    "Grandma's Golden Wok Pork Gyoza",
    "Blu Gourmet Pearl Couscous 400g",
    "Chicken Southern Fried Thigh Burger",
    "Southern Style Buttermilk Chicken Thigh Fillet Burgers",
]
_produce_keywords = [
    "Apples approx each",
    "Apples each",
    "Brown Onion",
    "Brown Onions",
    "Capsicum approx",
    "Capsicum approx. Each",
    "Carrot",
    "Carrots loose prepacked",
    "Cherry Tomatoes",
    "Coles Hass Avocados each",
    "Coles Sweet Gold Potatoes Loose approx. 450g each",
    "Diced Tomato",
    "Green Zucchini",
    "Hass Avocado",
    "Odd Bunch Capsicum",
    "Odd Bunch Zucchini",
    "Potatoes",
    "Pumpkin approx. each",
    "Pumpkin cut each",
    "Raspberries",
    "Raspberry",
    "Red Onion",
    "Strawberries",
    "Strawberry",
    "Sweet Potato",
    "Tomatoes",
    "White Potato",
    "tomato tomatoes",
]

_mock_keywords = (
    _original_keywords + _special_keywords + _generated_keywords + _merchant_unique_keywords + _produce_keywords
)


def test_merchant():
    bulk_search = search.BulkSearch(_mock_keywords)

    # Assert expect number of results
    for search_results in bulk_search.searches:
        assert len(search_results.results) == len(merchants.Merchants)
