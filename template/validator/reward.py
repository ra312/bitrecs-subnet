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


def does_sku_exist(sku: str, context: List[Product]) -> bool:
    """
    Check if sku exists in the context
    """
    if not sku or not context:
        return False
    if len(context) == 0:
        return False
    for product in context:
        if product.sku.lower().strip() == sku.lower().strip():
            return True
    return False   


def reward(num_recs: int, ground_truth: BitrecsRequest, response: BitrecsRequest) -> float:
    """
    Reward the miner response to the BitrecsRequest 

    Nubmer of recommendations should match the requested number of recommendations   

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
        #["{'sku': '24-UG06', 'name': 'Affirm Water Bottle', 'price': 7.0}", 
        #"{'sku': '24-WG084', 'name': 'Sprite Foam Yoga Brick', 'price': 5.0}", 
        store_catalog: list[Product] = json.loads(ground_truth.context)
        #bt.logging.info(f"** reward context: {store_catalog}")
        bt.logging.info(f"** reward response results: {response.results}")

        for result in response.results:            
            try:             
                result = result.replace("\'", "\"")
                product: Product = json.loads(result)
                bt.logging.info(f"** {response.miner_uid} reward product: {product}")
                sku = product.sku
                # Check if sku exists in the context
                if not does_sku_exist(sku, store_catalog):
                    bt.logging.info(f"Miner has invalid results: {response.miner_hotkey}")
                    return 0.01

            except Exception as e:
                bt.logging.info(f"JSON ERROR: {e}, miner data: {response.miner_hotkey}")
                return 0.0

        score = 0.80
        
        bt.logging.info(f"In reward, score: {score}, num_recs: {num_recs}, miner's data': {response.miner_hotkey}")

        return score
    except Exception as e:        
        bt.logging.info(f"Error in rewards: {e}, miner data: {response}")
        return None


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

    #for each response, calculate the reward

    #remove no results records - score them all 0

    #of the ones that have results, check if the number of results is equal to the number of recommendations

    #if the skus are not in the context, score them 0

    #ensure the skus exist in the context

    #order the remainign results by time spend dendrite_time 

    #select the best performing response as the winner

    # scored_candidates = [r for r in responses if r is not None and r.results is not None and len(r.results) > 0]    

    # zero_scored_candidates = [r for r in responses if r is None or r.results is None or len(r.results) < 1]   

    if num_recs < 1 or num_recs > 20:
        bt.logging.info(f"Invalid number of recommendations: {num_recs}")
        raise ValueError("configuration of num_recs is invalid")
    
    for r in responses:
        bt.logging.info(f"** get_rewards response: {r.miner_uid}")
        #bt.logging.info(f"** get_rewards headers: {r.to_headers()}")
        headers = r.to_headers()
        axon_time = -1
        dendrite_time = -1
        if "bt_header_axon_process_time" in headers:
            axon_time = headers["bt_header_axon_process_time"]
        if "bt_header_dendrite_process_time" in headers:
            dendrite_time = headers["bt_header_dendrite_process_time"]

        bt.logging.info(f"** get_rewards axon_time: {r.miner_uid}:{axon_time}")
        bt.logging.info(f"** get_rewards dendrite_time: {r.miner_uid}:{dendrite_time}")

    
    return np.array(
        [reward(num_recs, ground_truth, response) for response in responses], dtype=float
    )
    


