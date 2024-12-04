
import json
from dataclasses import dataclass
import bittensor as bt


@dataclass
class Product:
    sku: str
    name: str
    price: float

    @staticmethod
    def try_parse_context(context: str) -> list["Product"]:
        try:
            store_catalog: list[Product] = json.loads(context)
            return store_catalog
        except Exception as e:
            bt.logging.error(f"try_parse_context Exception: {e}")
            return []
    