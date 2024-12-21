import json
import json_repair
import jsonschema
import pytest

from template.commerce.product import CatalogProvider, Product
from template.llms.prompt_factory import PromptFactory

def test_basic_parsing():
    single_rec = "{'sku': '24-UG01', 'name': 'Quest Lumaflex&trade; Band', 'price': '19'}"
    single_rec2 = "{'sku': '24-UG02', 'name': 'Pursuit Lumaflex&trade; Tone Band', 'price': '16'}"
    single_rec3 = "{'sku': '24-MG05', 'name': 'Cruise Dual Analog Watch', 'price': '55'}"
    multi_rec = [single_rec, single_rec2, single_rec3]
    final_recs = [json.loads(idx.replace("'", '"')) for idx in multi_rec]
    print(final_recs)    
    assert len(multi_rec) == len(final_recs)    


def test_basic_parsing2():
    results =  ["{'sku': '24-WG088', 'name': 'Sprite Foam Roller'}",
                 "{'sku': '24-WG084', 'name': 'Sprite Foam Yoga Brick'}",
                   "{'sku': '24-UG01', 'name': 'Quest Lumaflex&trade; Band'}", 
                   '{\'sku\': \'24-UG05\', \'name\': "Go-Get\'r Pushup Grips"}', 
                   "{'sku': '24-UG02', 'name': 'Pursuit Lumaflex&trade; Tone Band'}", 
                   "{'sku': '24-UG07', 'name': 'Dual Handle Cardio Ball'}"]

    final = []
    for idx in results:        
        fixed1 = json_repair.repair_json(idx, logging=False)  
        print(f"fixed: {fixed1}")
        product = json_repair.loads(fixed1)        
        final.append(product)    
    print("FINAL RESULTS")
    print(final)
    assert len(results) == len(final)


def test_schema_validation():
    broken_json =  ["{'sku': '24-WG088', 'name': 'Sprite Foam Roller'}",
                 "{'sku': '24-WG084', 'name': 'Sprite Foam Yoga Brick'}",
                   "{'sku': '24-UG01', 'name': 'Quest Lumaflex&trade; Band'}", 
                   '{\'sku\': \'24-UG05\', \'name\': "Go-Get\'r Pushup Grips"}', 
                   "{'sku': '24-UG02', 'name': 'Pursuit Lumaflex&trade; Tone Band'}", 
                   "{'sku': '24-UG07', 'name': 'Dual Handle Cardio Ball'}"]
    
    partial_json =  ["{'sku': '24-WG088', 'name': 'Sprite Foam Roller'}",
                 "{'sku': '24-WG084', 'name': 'Sprite Foam Yoga Brick', 'price': 5.00}",
                   "{'sku': '24-UG01', 'name': 'Quest Lumaflex&trade; Band'}", 
                   '{\'sku\': \'24-UG05\', \'name\': "Go-Get\'r Pushup Grips"}', 
                   "{'sku': '24-UG02', 'name': 'Pursuit Lumaflex&trade; Tone Band'}", 
                   "{'sku': '24-UG07', 'name': 'Dual Handle Cardio Ball', 'price': '19'}"]
    
    good_json =  ["{'sku': '24-UG03', 'name': 'Harmony Lumaflex&trade; Strength Band Kit', 'price': '22'}", 
                "{'sku': '24-WG088', 'name': 'Sprite Foam Roller', 'price': '19'}",
                  "{'sku': '24-MB04', 'name': 'Strive Shoulder Pack', 'price': '32'}", 
                  "{'sku': '24-UG01', 'name': 'Quest Lumaflex&trade; Band', 'price': '19'}", 
                  '{\'sku\': \'24-UG05\', \'name\': "Go-Get\'r Pushup Grips", \'price\': \'19\'}', 
                  "{'sku': '24-WG084', 'name': 'Sprite Foam Yoga Brick', 'price': '5'}"]
    
    schema = {
        "type": "object",
        "properties": {
            "sku": {"type": "string"},
            "name": {"type": "string"},
            "price": {"type": "string"}
        },
        "required": ["sku", "name", "price"]
    }

    broken_count = 0
    for item in broken_json:
        try:
            thing = json_repair.loads(item)
            jsonschema.validate(thing, schema)
            broken_count += 1
        except json.decoder.JSONDecodeError as e:            
            continue
        except jsonschema.exceptions.ValidationError as e:            
            continue
    #print(broken_count)
    assert broken_count == 0

    partial_count = 0
    for item in partial_json:
        try:
            thing = json_repair.loads(item)
            jsonschema.validate(thing, schema)
            partial_count += 1
        except json.decoder.JSONDecodeError as e:            
            continue
        except jsonschema.exceptions.ValidationError as e:            
            continue
    
    assert partial_count == 1


    good_count = 0
    for item in good_json:
        try:
            thing = json_repair.loads(item)
            jsonschema.validate(thing, schema)
            good_count += 1
        except json.decoder.JSONDecodeError as e:            
            continue
        except jsonschema.exceptions.ValidationError as e:            
            continue

    assert good_count == len(good_json)


def test_load_1k_raw():
    rows = []
    with open("./tests/data/amazon/fashion/amazon_fashion_sample_1000.json", "r") as f:
        data = f.read()
        rows = json_repair.loads(data)    
    print(f"loaded {len(rows)} records")
    assert len(rows) == 1000


def test_load_5k_raw():
    rows = []
    with open("./tests/data/amazon/fashion/amazon_fashion_sample_5000.json", "r") as f:
        data = f.read()
        rows = json_repair.loads(data)    
    print(f"loaded {len(rows)} records")
    assert len(rows) == 5000


def test_parse_1k_into_products():
    with open("./tests/data/amazon/fashion/amazon_fashion_sample_1000.json", "r") as f:
        data = f.read()    
    products = Product.try_parse_context(data)
    print(f"loaded {len(products)} records")    
    assert len(products) == 1000


def test_parse_5k_into_products():
    with open("./tests/data/amazon/fashion/amazon_fashion_sample_5000.json", "r") as f:
        data = f.read()    
    products = Product.try_parse_context(data)
    print(f"loaded {len(products)} records")    
    assert len(products) == 5000


def test_parse_20k_into_products():
    with open("./tests/data/amazon/fashion/amazon_fashion_sample_20000.json", "r") as f:
        data = f.read()    
    products = Product.try_parse_context(data)
    print(f"loaded {len(products)} records")    
    assert len(products) == 20000



def test_parse_1k_products_have_missing_fields():
    with open("./tests/data/amazon/fashion/amazon_fashion_sample_1000.json", "r") as f:
        data = f.read()    
    products = Product.try_parse_context(data)
    print(f"loaded {len(products)} records")       
    assert len(products) == 1000

    broken = False
    for product in products:
        if not hasattr(product, "sku"):
            broken = True
            break
        if not hasattr(product, "name"):
            broken = True
            break
        if not hasattr(product, "price"):
            broken = True
            break

    assert broken # should be broken

            
def test_convert_1k_amazon_to_bitrecs():
    with open("./tests/data/amazon/fashion/amazon_fashion_sample_1000.json", "r") as f:
        data = f.read()    
    products = Product.convert(data, CatalogProvider.AMAZON)
    print(f"converted {len(products)} records")       
    assert len(products) == 907

    dupe_count = Product.get_dupe_count(products)
    print(f"dupe count: {dupe_count}")
    assert dupe_count == 61

    for product in products:
        if not hasattr(product, "sku"):
            assert False
        if not hasattr(product, "name"):
            assert False
        if not hasattr(product, "price"):
            assert False


def test_convert_5k_amazon_to_bitrecs():
    with open("./tests/data/amazon/fashion/amazon_fashion_sample_5000.json", "r") as f:
        data = f.read()    
    products = Product.convert(data, CatalogProvider.AMAZON)
    print(f"converted {len(products)} records")       
    assert len(products) == 4544

    dupe_count = Product.get_dupe_count(products)
    print(f"dupe count: {dupe_count}")
    assert dupe_count == 416

    for product in products:
        if not hasattr(product, "sku"):
            assert False
        if not hasattr(product, "name"):
            assert False
        if not hasattr(product, "price"):
            assert False



def test_convert_20k_amazon_to_bitrecs():
    with open("./tests/data/amazon/fashion/amazon_fashion_sample_20000.json", "r") as f:
        data = f.read()    
    products = Product.convert(data, CatalogProvider.AMAZON)
    print(f"converted {len(products)} records")       
    assert len(products) == 18088

    dupe_count = Product.get_dupe_count(products)
    print(f"dupe count: {dupe_count}")
    assert dupe_count == 3324

    for product in products:
        if not hasattr(product, "sku"):
            assert False
        if not hasattr(product, "name"):
            assert False
        if not hasattr(product, "price"):
            assert False


def test_convert_1k_woocommerce_to_bitrecs():
    woo_catalog = "./tests/data/woocommerce/product_catalog.csv" #2038 records
    catalog = PromptFactory.tryload_catalog_to_json(CatalogProvider.WOOCOMMERCE, woo_catalog)
    products = Product.convert(catalog, CatalogProvider.WOOCOMMERCE)
    print(f"converted {len(products)} records")       
    assert len(products) == 2038

    for product in products:
        if not hasattr(product, "sku"):
            assert False
        if not hasattr(product, "name"):
            assert False
        if not hasattr(product, "price"):
            assert False


def test_convert_1k_shopify_to_bitrecs():
    shopify_catalog = "./tests/data/shopify/electronics/shopify_products.csv" #824 records
    catalog = Product.tryload_catalog_to_json(CatalogProvider.SHOPIFY, shopify_catalog)
    products = Product.convert(catalog, CatalogProvider.SHOPIFY)
    print(f"converted {len(products)} records")       
    assert len(products) == 805

    for product in products:
        if not hasattr(product, "sku"):
            assert False
        if not hasattr(product, "name"):
            assert False
        if not hasattr(product, "price"):
            assert False
    
    for p in products:
        print(p)
    


   

   