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
import numpy as np
import time
import bittensor as bt
from template.protocol import BitrecsRequest
from typing import List


def reward(num_recs: int, response: BitrecsRequest) -> float:
    """
    Reward the miner response to the BitrecsRequest 

    Nubmer of recommendations should match the requeted number of recommendations   

    Returns:
    - float: The reward value for the miner.
    """
    
    print("*************** REWARD *************************")
    # TODO check format of response as they are from LLMs
    try:

        if response == {} or None:
            score = 0
        elif len(response.results) < 1:
            score = 0
        elif len(response.results) < num_recs:
            return 0.01
        elif len(response.results) == num_recs:
            score = 0.80
        elif len(response.results) > num_recs:
            score = 0.02
        else:
            score = 0
        
        #bt.logging.info(f"In reward, score: {score}, num_recs: {num_recs}, miner's data': {response.miner_hotkey}")

        return score
    except Exception as e:        
        bt.logging.info(f"Error in rewards: {e}, miner data: {response}")
        return None


def get_rewards(
    num_recs: int,
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
    
    for r in responses:
        bt.logging.info(f"** get_rewards response: {r.miner_uid}")
    
    return np.array(
        [reward(num_recs, response) for response in responses], dtype=float
    )    
    
