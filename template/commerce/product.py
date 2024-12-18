
import json
import bittensor as bt
from dataclasses import dataclass
from enum import Enum


class CatalogProvider(Enum):
    SHOPIFY = 1
    AMAZON = 2
    WOOCOMMERCE = 3
    BIGCOMMERCE = 4


@dataclass
class Product:
    sku: str
    name: str
    price: float


    @staticmethod
    def try_parse_context(context: str) -> list["Product"]:
        """
        Default converter expects a json array of products with sku/name/price fields

        """
        try:
            store_catalog: list[Product] = json.loads(context)
            return store_catalog
        except Exception as e:
            bt.logging.error(f"try_parse_context Exception: {e}")
            return []
        
        
    # @staticmethod
    # def deduplicate_list(obj_list):
    #     seen = set()
    #     return [x for x in obj_list if not (id(x) in seen or seen.add(id(x)))]
    
    @staticmethod
    def dedupe(products: list["Product"]):
        seen = set()
        for product in products:
            sku = product.sku
            if sku in seen:
                continue
            seen.add(sku)
        return [product for product in products if product.sku in seen]
        
        
    @staticmethod
    def convert(context: str, provider: CatalogProvider) -> list["Product"]:
        """
            context should be the store catalog in Product format (sku, name, price)            

        """
        match provider:
            case CatalogProvider.SHOPIFY:
                return ShopifyConverter().convert(context)                
            case CatalogProvider.AMAZON:
                return AmazonConverter().convert(context)
            case CatalogProvider.WOOCOMMERCE:
                return WoocommerceConverter().convert(context)
            case CatalogProvider.BIGCOMMERCE:
                return BigcommerceConverter().convert(context)
            case _:
                raise NotImplementedError("invalid provider")



class WoocommerceConverter:
    
    # def convert(self, context: str) -> list["Product"]:
    #     return Product.try_parse_context(context)
    
    def convert(self, context: str) -> list["Product"]:
        """
        converts from product_catalog.csv converted to json format

        """
        result : list[Product] = []
        for p in json.loads(context):
            try:
                sku = p.get("sku")
                name = p.get("name")
                price = p.get("price")
                # if not sku or not name or not price:
                #     continue
                result.append(Product(sku=sku, name=name, price=price))
            except Exception as e:
                bt.logging.error(f"WoocommerceConverter.convert Exception: {e}")
                continue
        return result
        

    
class AmazonConverter:
    
    def convert(self, context: str) -> list["Product"]:
        """
        converts from amazon_fashion_sample_1000.json format

        """
        result : list[Product] = []
        for p in json.loads(context):
            try:
                sku = p.get("asin")
                if p["metadata"]:
                    name = p["metadata"].get("title")
                    price = p["metadata"].get("price")
                if not sku or not name or not price:
                    continue
                result.append(Product(sku=sku, name=name, price=price))
            except Exception as e:
                bt.logging.error(f"AmazonConverter.convert Exception: {e}")
                continue
        return result
    

class ShopifyConverter:
    
    def convert(self, context: str) -> list["Product"]:
        raise NotImplementedError("Shopify not implemented")
    

    
class BigcommerceConverter:
    
    def convert(self, context: str) -> list["Product"]:
        raise NotImplementedError("Bigcommerce not implemented")