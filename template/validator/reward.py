# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

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
from template.protocol import BitrecsRequest
from template.llms.prompt_factory import PromptFactory
from typing import List
from dataclasses import dataclass

@dataclass
class Product:
    sku: str
    name: str
    price: float

ALPHA_TIME_DECAY = 0.05


def does_sku_exist(sku: str, context: List[Product]) -> bool:
    """
    Check if sku exists in the context
    """
    if not sku or not context:
        return False
    if len(context) == 0:
        return False
    for product in context:
        if product["sku"].lower().strip() == sku.lower().strip():
            return True
    return False   


def reward(num_recs: int, ground_truth: BitrecsRequest, response: BitrecsRequest) -> float:
    """
    Reward the miner response to the BitrecsRequest 

    Nubmer of recommendations should match the requested number of recommendations   
    Unique recommendations in the response is expected
    Malformed json or bad skus are penalized

    Returns:
    - float: The reward value for the miner.
    """
    
    print("*************** REWARD *************************")
    # TODO check format of response as they are from LLMs

    try:
        score = 0.00
        if len(response.results) != num_recs:            
            return 0.00      

        # Check each result to exist in the context
        #["{'sku': '24-UG06', 'name': 'Affirm Water Bottle', 'price': 7.0}"]         
        store_catalog: list[Product] = json.loads(ground_truth.context)
        #bt.logging.info(f"** reward context: {store_catalog}")
        bt.logging.info(f"** reward response results: {response.results}")

        valid_items = set()
        for result in response.results:            
            try:             
                result = result.replace("\'", "\"")
                product: Product = json.loads(result)
                bt.logging.info(f"** {response.miner_uid} reward product: {product}")
                sku = product["sku"]
                if sku in valid_items:
                    bt.logging.info(f"Miner has duplicate results: {response.miner_hotkey}")
                    return 0.0               
                
                # Check if sku exists in the context
                if not does_sku_exist(sku, store_catalog):
                    bt.logging.info(f"Miner has invalid results: {response.miner_hotkey}")
                    return 0.01
                
                valid_items.add(sku)

            except Exception as e:
                bt.logging.info(f"JSON ERROR: {e}, miner data: {response.miner_hotkey}")
                return 0.0

        if len(valid_items) != num_recs:
            bt.logging.info(f"Miner has invalid number of valid_items: {response.miner_hotkey}")
            return 0.0

        score = 0.80        
        bt.logging.info(f"In reward, score: {score}, num_recs: {num_recs}, miner's data': {response.miner_hotkey}")

        #Check ttl time        
        headers = response.to_headers()
        if "bt_header_dendrite_process_time" in headers:
            dendrite_time = headers["bt_header_dendrite_process_time"] #0.000132  1.2
            score = score - ALPHA_TIME_DECAY * float(dendrite_time)
        else:
            bt.loggin.error(f"Error in reward: dendrite_time not found in headers")
            return 0.0

        return score
    except Exception as e:        
        bt.logging.info(f"Error in rewards: {e}, miner data: {response}")
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
    - responses (List[float]): A list of responses from the miner.

    Returns:
    - np.ndarray: An array of rewards for the given query and responses.
    """

    if num_recs < 1 or num_recs > 20:
        bt.logging.info(f"Invalid number of recommendations: {num_recs}")
        raise ValueError("configuration of num_recs is invalid")
        
    return np.array(
        [reward(num_recs, ground_truth, response) for response in responses], dtype=float
    )
    


