# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2024 Bitrecs

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time
import json
import numpy as np
import bittensor as bt
import jsonschema
import json_repair
from template.protocol import BitrecsRequest
from template.llms.prompt_factory import PromptFactory
from typing import List
from template.commerce.product import Product

ALPHA_TIME_DECAY = 0.05
MIN_CATALOG_SIZE = 10

def does_sku_exist(sku: str, store_catalog: List[Product]) -> bool:
    """
    Check if sku exists in the context
    """
    if not sku or not store_catalog:
        return False
    if len(store_catalog) == 0:
        return False
    for product in store_catalog:
        if product["sku"].lower().strip() == sku.lower().strip():
            return True
    return False
   

def validate_result_schema(num_recs: int, results: list) -> bool:
    """
    Ensure results from Miner match the required schema
    """
    if num_recs < 1 or num_recs > 20:
        return False
    if len(results) != num_recs:
        bt.logging.error("Error validate_result_schema mismatch")
        return False
    
    schema = {
        "type": "object",
        "properties": {
            "sku": {"type": "string"},
            "name": {"type": "string"},
            "price": {"type": "string"}
        },
        "required": ["sku", "name", "price"]
    }

    count = 0
    for item in results:
        try:            
            thing = json_repair.loads(item)            
            validated = jsonschema.validate(thing, schema)
            if validated is not None:
                return False            
            count += 1
        except json.decoder.JSONDecodeError as e:            
            bt.logging.trace(f"JSON JSONDecodeError ERROR: {e}")
            break
        except jsonschema.exceptions.ValidationError as e:            
            bt.logging.trace(f"JSON ValidationError ERROR: {e}")
            break
        except Exception as e:            
            bt.logging.trace(f"JSON Exception ERROR: {e}")
            break

    return count == len(results)


def reward(num_recs: int, store_catalog: list[Product], response: BitrecsRequest) -> float:
    """
    Score the Miner's response to the BitrecsRequest 

    Nubmer of recommendations should match the requested number of recommendations
    Recommendations must exist in the original catalog
    Unique recommendations in the response is expected
    Malformed JSON or invliad skus will result in a 0.0 reward

    Returns:
    - float: The reward value for the miner.
    """    
    
    bt.logging.trace("*************** VALIDATOR REWARD *************************")

    try:
        score = 0.0
        if len(response.results) != num_recs:            
            return 0.0

        if not validate_result_schema(num_recs, response.results):
            bt.logging.error(f"Miner has invalid schema results: {response.miner_hotkey}")
            return 0.0

        valid_items = set()
        for result in response.results:
            try:             
                result = result.replace("\'", "\"")
                product: Product = json.loads(result)
                #bt.logging.trace(f"{response.miner_uid} response product: {product}")
                sku = product["sku"]
                if sku in valid_items:
                    bt.logging.warning(f"Miner has duplicate results: {response.miner_hotkey}")
                    return 0.0               
                
                # Check if sku exists in the context
                if not does_sku_exist(sku, store_catalog):
                    bt.logging.warning(f"Miner has invalid results: {response.miner_hotkey}")
                    return 0.00
                
                valid_items.add(sku)

            except Exception as e:
                bt.logging.error(f"JSON ERROR: {e}, miner data: {response.miner_hotkey}")
                return 0.0

        if len(valid_items) != num_recs:
            bt.logging.warning(f"Miner has invalid number of valid_items: {response.miner_hotkey}")
            return 0.0

        score = 0.80        
        bt.logging.info(f"In reward, score: {score}, num_recs: {num_recs}, miner's data': {response.miner_hotkey}")

        #Check ttl time        
        headers = response.to_headers()
        if "bt_header_dendrite_process_time" in headers:
            dendrite_time = headers["bt_header_dendrite_process_time"] #0.000132  1.2
            score = score - ALPHA_TIME_DECAY * float(dendrite_time)
        else:
            bt.logging.error(f"Error in reward: dendrite_time not found in headers")
            return 0.0

        return score
    except Exception as e:        
        bt.logging.error(f"Error in rewards: {e}, miner data: {response}")
        return 0.0


def get_rewards(
    num_recs: int,
    ground_truth: BitrecsRequest,
    responses: List[BitrecsRequest],
) -> np.ndarray:
    """
    Returns an array of rewards for the given query and responses.

    Args:
    - num_recs (int): The number of results expected per miner response.
    - ground_truth (BitrecsRequest): The original ground truth which contains the catalog and query
    - responses (List[float]): A list of responses from the miner.

    Returns:
    - np.ndarray: An array of rewards for the given query and responses.
    """

    if num_recs < 1 or num_recs > 20:
        bt.logging.error(f"Invalid number of recommendations: {num_recs}")
        return np.zeros(len(responses), dtype=float)        
    
    store_catalog: list[Product] = Product.try_parse_context(ground_truth.context)
    if len(store_catalog) < MIN_CATALOG_SIZE:
        bt.logging.error(f"Invalid catalog size: {len(store_catalog)}")
        return np.zeros(len(responses), dtype=float)
        
    return np.array(
        [reward(num_recs, store_catalog, response) for response in responses], dtype=float
    )


