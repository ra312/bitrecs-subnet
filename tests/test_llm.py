import ast
import json
import os
from dataclasses import asdict
import random
from typing import Counter

import pytest
from template.commerce.product import CatalogProvider, Product
from template.llms.factory import LLM, LLMFactory
from template.llms.prompt_factory import PromptFactory

os.environ["NEST_ASYNCIO"] = "0"

LOCAL_OLLAMA_URL = "http://10.0.0.40:11434/api/chat"


def product_woo():
    woo_catalog = "./tests/data/product_catalog.csv" #2038 records
    catalog = PromptFactory.tryload_catalog_to_json(woo_catalog)
    products = Product.convert(catalog, CatalogProvider.WOOCOMMERCE)
    return products

def product_1k():
    with open("./tests/data/amazon_fashion_sample_1000.json", "r") as f:
        data = f.read()    
    products = Product.convert(data, CatalogProvider.AMAZON)
    return products

def product_5k():
    with open("./tests/data/amazon_fashion_sample_5000.json", "r") as f:
        data = f.read()    
    products = Product.convert(data, CatalogProvider.AMAZON)
    return products

def product_20k():
    with open("./tests/data/amazon_fashion_sample_20000.json", "r") as f:
        data = f.read()    
    products = Product.convert(data, CatalogProvider.AMAZON)
    return products


def test_call_local_llm_with_woo_catalog():
    products = product_woo()
    print(f"loaded {len(products)} records")
    assert len(products) == 2038
    #print(products)
    dd = Product.get_dupe_count(products)
    print(f"dupe count: {dd}")
    assert dd == 0
    
    #24-WB02 =Compete Track Tote
    #The Compete Track Tote holds a host of exercise supplies with ease. Stash your towel, jacket and street shoes inside. 
    # Tuck water bottles in easy-access external spaces. 
    # Perfect for trips to gym or yoga studio, with dual top handles for convenience to and from.
    
    user_prompt = "24-WB02"
    num_recs = 7
    debug_prompts = False

    match = [products for products in products if products.sku == user_prompt][0]
    print(f"Getting rec for: {match}")

    context = json.dumps([asdict(products) for products in products])
    factory = PromptFactory(sku=user_prompt, 
                            context=context, 
                            num_recs=num_recs, 
                            load_catalog=False, 
                            debug=debug_prompts)
    
    prompt = factory.generate_prompt()
    #print(prompt)

    os.environ["OLLAMA_LOCAL_URL"] = LOCAL_OLLAMA_URL
    model = "llama3.1"
    llm_response = LLMFactory.query_llm(server=LLM.OLLAMA_LOCAL,
                                 model=model,
                                 system_prompt="You are a helpful assistant", 
                                 temp=0.0, user_prompt=prompt)
    #print(llm_response)    
    parsed_recs = PromptFactory.tryparse_llm(llm_response)
    print(f"parsed {len(parsed_recs)} records")
    print(parsed_recs)
    
    assert len(parsed_recs) == num_recs

    #check uniques
    skus = [item['sku'] for item in parsed_recs]
    counter = Counter(skus)
    for sku, count in counter.items():
        print(f"{sku}: {count}")
        assert count == 1




def test_call_local_llm_with_1k():
    products = product_1k()
    print(f"loaded {len(products)} records")
    assert len(products) == 907
    
    dd = Product.get_dupe_count(products)
    print(f"dupe count: {dd}")
    assert dd == 61
    
    #B07BG1CZ8X = iJuqi Mom Gifts from Daughter Son - 3PCS Stainless Steel Expendable Motivational 
    # #Charm Bangle Bracelets Set for Mother's Day, Birthday Gifts for Mom, Mother Jewelry for Christmas (Silver)
    
    user_prompt = "B07BG1CZ8X"
    num_recs = 5
    debug_prompts = False

    match = [products for products in products if products.sku == user_prompt][0]
    print(match)

    context = json.dumps([asdict(products) for products in products])
    factory = PromptFactory(sku=user_prompt, 
                            context=context, 
                            num_recs=num_recs, 
                            load_catalog=False, 
                            debug=debug_prompts)
    
    prompt = factory.generate_prompt()
    #print(prompt)

    os.environ["OLLAMA_LOCAL_URL"] = LOCAL_OLLAMA_URL
    model = "llama3.1"
    llm_response = LLMFactory.query_llm(server=LLM.OLLAMA_LOCAL,
                                 model=model, 
                                 system_prompt="You are a helpful assistant", 
                                 temp=0.0, user_prompt=prompt)
    #print(llm_response)    
    parsed_recs = PromptFactory.tryparse_llm(llm_response)   
    print(f"parsed {len(parsed_recs)} records")
    print(parsed_recs)
    
    assert len(parsed_recs) == num_recs

    #check uniques
    skus = [item['sku'] for item in parsed_recs]
    counter = Counter(skus)
    for sku, count in counter.items():
        print(f"{sku}: {count}")
        assert count == 1
    
  
def test_call_local_llm_with_5k():
    products = product_5k()
    print(f"loaded {len(products)} records")
    assert len(products) == 4544

    dd = Product.get_dupe_count(products)
    print(f"dupe count: {dd}")
    assert dd == 416

    products = Product.dedupe(products)
    print(f"after de-dupe: {len(products)} records")

    #B07BG1CZ8X = iJuqi Mom Gifts from Daughter Son - 3PCS Stainless Steel Expendable Motivational 
    # #Charm Bangle Bracelets Set for Mother's Day, Birthday Gifts for Mom, Mother Jewelry for Christmas (Silver)
    
    user_prompt = "B07BG1CZ8X"
    num_recs = 6
    debug_prompts = False

    match = [products for products in products if products.sku == user_prompt][0]
    print(match)
    print(f"num_recs: {num_recs}")

    context = json.dumps([asdict(products) for products in products])
    factory = PromptFactory(sku=user_prompt, 
                            context=context, 
                            num_recs=num_recs, 
                            load_catalog=False, 
                            debug=debug_prompts)
    
    prompt = factory.generate_prompt()
    #print(prompt)

    os.environ["OLLAMA_LOCAL_URL"] = LOCAL_OLLAMA_URL
    model = "llama3.1"
    llm_response = LLMFactory.query_llm(server=LLM.OLLAMA_LOCAL,
                                 model=model, 
                                 system_prompt="You are a helpful assistant", 
                                 temp=0.0, user_prompt=prompt)
    #print(llm_response)    
    parsed_recs = PromptFactory.tryparse_llm(llm_response)   
    print(f"parsed {len(parsed_recs)} records")
    print(parsed_recs)
    
    assert len(parsed_recs) == num_recs

    #check uniques
    skus = [item['sku'] for item in parsed_recs]
    counter = Counter(skus)
    for sku, count in counter.items():
        print(f"{sku}: {count}")
        assert count == 1    


def test_call_local_llm_with_20k():
    raw_products = product_20k()
    print(f"loaded: {len(raw_products)} records")
    assert len(raw_products) == 18_088

    dd = Product.get_dupe_count(raw_products)
    print(f"dupe count: {dd}")
    #assert dd == 2106    

    products = Product.dedupe(raw_products)    
    print(f"after de-dupe: {len(products)} records")
   
    #B07BG1CZ8X = iJuqi Mom Gifts from Daughter Son - 3PCS Stainless Steel Expendable Motivational 
    # #Charm Bangle Bracelets Set for Mother's Day, Birthday Gifts for Mom, Mother Jewelry for Christmas (Silver)
    
    user_prompt = "B07BG1CZ8X"
    num_recs = 6
    debug_prompts = False

    match = [products for products in products if products.sku == user_prompt][0]
    print(match)    

    context = json.dumps([asdict(products) for products in products])
    factory = PromptFactory(sku=user_prompt, 
                            context=context, 
                            num_recs=num_recs, 
                            load_catalog=False, 
                            debug=debug_prompts)
    
    prompt = factory.generate_prompt()
    #print(prompt)

    os.environ["OLLAMA_LOCAL_URL"] = LOCAL_OLLAMA_URL
    #model = "llama3.1:70b" 
    #model = "qwen2.5:32b-instruct"  
    #model = "llama3.3:latest"    
    #model = "mistral-nemo"
    #model = "qwen2.5"
    model = "llama3.1"

    llm_response = LLMFactory.query_llm(server=LLM.OLLAMA_LOCAL,
                                 model=model,
                                 system_prompt="You are a helpful assistant", 
                                 temp=0.0, user_prompt=prompt)
    #print(llm_response)    
    parsed_recs = PromptFactory.tryparse_llm(llm_response)   
    print(f"parsed {len(parsed_recs)} records")
    print(parsed_recs)
  
    assert len(parsed_recs) == num_recs

    #check uniques
    skus = [item['sku'] for item in parsed_recs]
    counter = Counter(skus)
    for sku, count in counter.items():
        print(f"{sku}: {count}")
        assert count == 1


def test_call_local_llm_with_20k_llm_logic():
    raw_products = product_20k()
    print(f"loaded: {len(raw_products)} records")
    assert len(raw_products) == 18_088

    dd = Product.get_dupe_count(raw_products)
    print(f"dupe count: {dd}")
    #assert dd == 2106    

    products = Product.dedupe(raw_products)    
    print(f"after de-dupe: {len(products)} records")
   
    #B07BG1CZ8X = iJuqi Mom Gifts from Daughter Son - 3PCS Stainless Steel Expendable Motivational 
    # #Charm Bangle Bracelets Set for Mother's Day, Birthday Gifts for Mom, Mother Jewelry for Christmas (Silver)
    rp = random.choice(products)
    user_prompt = rp.sku

    #user_prompt = "B07BG1CZ8X"
    num_recs = random.choice([5, 6, 7, 8, 9, 10, 16, 20])
    #num_recs = 8

    debug_prompts = False

    match = [products for products in products if products.sku == user_prompt][0]
    print(match)    
    print(f"num_recs: {num_recs}")  

    context = json.dumps([asdict(products) for products in products])
    factory = PromptFactory(sku=user_prompt, 
                            context=context, 
                            num_recs=num_recs, 
                            load_catalog=False, 
                            debug=debug_prompts)
    
    prompt = factory.generate_prompt()
    #print(prompt)

    os.environ["OLLAMA_LOCAL_URL"] = LOCAL_OLLAMA_URL
    #model = "llama3.1:70b" 
    #model = "qwen2.5:32b-instruct"  
    #model = "llama3.3:latest"    
    #model = "mistral-nemo"
    #model = "qwen2.5"
    model = "llama3.1"

    llm_response = LLMFactory.query_llm(server=LLM.OLLAMA_LOCAL,
                                 model=model,
                                 system_prompt="You are a helpful assistant", 
                                 temp=0.0, user_prompt=prompt)
    #print(llm_response)    
    parsed_recs = PromptFactory.tryparse_llm(llm_response)   
    print(f"parsed {len(parsed_recs)} records")
    print(parsed_recs)
  
    assert len(parsed_recs) == num_recs  

    #check uniques
    skus = [item['sku'] for item in parsed_recs]
    counter = Counter(skus)
    for sku, count in counter.items():
        print(f"{sku}: {count}")
        assert count == 1

    assert user_prompt not in skus



@pytest.mark.skip(reason="skipped for now please ensure .env file has open router api key")
def test_call_open_router_with_20k_llm_logic():
    raw_products = product_20k()
    print(f"loaded: {len(raw_products)} records")
    assert len(raw_products) == 20_000

    dd = Product.get_dupe_count(raw_products)
    print(f"dupe count: {dd}")
    #assert dd == 2106    

    products = Product.dedupe(raw_products)    
    print(f"after de-dupe: {len(products)} records")
   
    #B07BG1CZ8X = iJuqi Mom Gifts from Daughter Son - 3PCS Stainless Steel Expendable Motivational 
    # #Charm Bangle Bracelets Set for Mother's Day, Birthday Gifts for Mom, Mother Jewelry for Christmas (Silver)
    rp = random.choice(products)
    user_prompt = rp.sku

    #user_prompt = "B07BG1CZ8X"
    num_recs = random.choice([5, 6, 7, 8, 9, 10, 16, 20])
    #num_recs = 8

    debug_prompts = False

    match = [products for products in products if products.sku == user_prompt][0]
    print(match)    
    print(f"num_recs: {num_recs}")  

    context = json.dumps([asdict(products) for products in products])
    factory = PromptFactory(sku=user_prompt, 
                            context=context, 
                            num_recs=num_recs, 
                            load_catalog=False, 
                            debug=debug_prompts)
    
    prompt = factory.generate_prompt()
    #print(prompt)


    from dotenv import load_dotenv
    load_dotenv() #LLMFactory needs this to load the api key

    model = "google/gemini-flash-1.5-8b"

    llm_response = LLMFactory.query_llm(server=LLM.OPEN_ROUTER,
                                 model=model,
                                 system_prompt="You are a helpful assistant", 
                                 temp=0.0, user_prompt=prompt)
    #print(llm_response)    
    parsed_recs = PromptFactory.tryparse_llm(llm_response)   
    print(f"parsed {len(parsed_recs)} records")
    print(parsed_recs)
  
    assert len(parsed_recs) == num_recs
  

    #check uniques
    skus = [item['sku'] for item in parsed_recs]
    counter = Counter(skus)
    for sku, count in counter.items():
        print(f"{sku}: {count}")
        assert count == 1

    assert user_prompt not in skus



@pytest.mark.skip(reason="skipped for now please ensure .env file has gemini api key")
def test_call_gemini_with_20k_llm_logic():
    raw_products = product_20k()
    print(f"loaded: {len(raw_products)} records")
    assert len(raw_products) == 20_000

    dd = Product.get_dupe_count(raw_products)
    print(f"dupe count: {dd}")
    #assert dd == 2106    

    products = Product.dedupe(raw_products)    
    print(f"after de-dupe: {len(products)} records")
   
    #B07BG1CZ8X = iJuqi Mom Gifts from Daughter Son - 3PCS Stainless Steel Expendable Motivational 
    # #Charm Bangle Bracelets Set for Mother's Day, Birthday Gifts for Mom, Mother Jewelry for Christmas (Silver)
    rp = random.choice(products)
    user_prompt = rp.sku

    #user_prompt = "B07BG1CZ8X"
    num_recs = random.choice([5, 6, 7, 8, 9, 10, 16, 20])
    #num_recs = 8

    debug_prompts = False

    match = [products for products in products if products.sku == user_prompt][0]
    print(match)    
    print(f"num_recs: {num_recs}")  

    context = json.dumps([asdict(products) for products in products])
    factory = PromptFactory(sku=user_prompt, 
                            context=context, 
                            num_recs=num_recs, 
                            load_catalog=False, 
                            debug=debug_prompts)
    
    prompt = factory.generate_prompt()
    #print(prompt)

    from dotenv import load_dotenv
    load_dotenv() #LLMFactory needs this to load the api key

    model = "gemini-2.0-flash-exp"

    llm_response = LLMFactory.query_llm(server=LLM.GEMINI,
                                 model=model,
                                 system_prompt="You are a helpful assistant", 
                                 temp=0.0, user_prompt=prompt)
    #print(llm_response)    
    parsed_recs = PromptFactory.tryparse_llm(llm_response)   
    print(f"parsed {len(parsed_recs)} records")
    print(parsed_recs)
  
    assert len(parsed_recs) == num_recs
  

    #check uniques
    skus = [item['sku'] for item in parsed_recs]
    counter = Counter(skus)
    for sku, count in counter.items():
        print(f"{sku}: {count}")
        assert count == 1

    assert user_prompt not in skus