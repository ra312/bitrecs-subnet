import json
import re
import bittensor as bt
from typing import Counter
from pydantic import BaseModel
from abc import abstractmethod
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
    price: str


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
        
   
    @staticmethod
    def get_dupe_count(products: list["Product"]) -> int:
        try:
            if not products or len(products) == 0:
                return 0
            sku_counts = Counter(product.sku for product in products)
            return sum(count - 1 for count in sku_counts.values() if count > 1)
        except AttributeError:
            return 0
        
    
    @staticmethod
    def dedupe(products: list["Product"]) -> list["Product"]:
        unique_products = {}
        for product in products:
            if product.sku not in unique_products:
                unique_products[product.sku] = product
        return list(unique_products.values())
        
        
    @staticmethod
    def convert(context: str, provider: CatalogProvider) -> list["Product"]:
        """
            Convert a raw store catalog json in Products

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


class BaseConverter(BaseModel):
    
    @abstractmethod
    def convert(self, context: str) -> list["Product"]:
        raise NotImplementedError("BaseConverter not implemented")
    
    def clean(self, raw_value: str) -> str:        
        result = re.sub(r"[^A-Za-z ]", "", raw_value)
        return result.strip()
    

class WoocommerceConverter(BaseConverter):    
  
    def convert(self, context: str) -> list["Product"]:
        """
        converts from product_catalog.csv to Products

        args:
            context: str - woocommerce product export converted to json            

        """
        result : list[Product] = []
        for p in json.loads(context):
            try:
                sku = p.get("sku")
                name = p.get("name")
                price = p.get("price", "0.00")             
                if not sku or not name:
                    continue
                if price is None or price == 'None':
                    price = "0.00"
                price = str(price)
                name = self.clean(name)
                result.append(Product(sku=sku, name=name, price=price))
            except Exception as e:
                bt.logging.error(f"WoocommerceConverter.convert Exception: {e}")
                continue
        return result
        

    
class AmazonConverter(BaseConverter):
    
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
                    price = p["metadata"].get("price", "0.00")
                if not sku or not name:
                    continue
                if price is None or price == 'None':                    
                    price = "0.00"
                price = str(price)
                name = self.clean(name)
                result.append(Product(sku=sku, name=name, price=price))
            except Exception as e:
                bt.logging.error(f"AmazonConverter.convert Exception: {e}")
                continue
        return result
    

class ShopifyConverter(BaseConverter):
    
    def convert(self, context: str) -> list["Product"]:
        raise NotImplementedError("Shopify not implemented")
    

    
class BigcommerceConverter(BaseConverter):
    
    def convert(self, context: str) -> list["Product"]:
        raise NotImplementedError("Bigcommerce not implemented")