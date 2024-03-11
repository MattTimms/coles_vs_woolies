from . import coles, iga, woolworths
from .base import MerchantClass, MerchantName, ProductClass, SearchResultPage

Merchants: list[MerchantClass] = [coles.Coles(), iga.IGA(), woolworths.Woolworths()]
merchant_names: set[MerchantName] = {"coles", "iga", "woolworths"}

__all__ = ["coles", "iga", "woolworths", "ProductClass", "SearchResultPage", "MerchantName", "Merchants"]
