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
    Reward the miner response to the ProductRecRequest 

    Nubmer of recommendations should match the requeted number of recommendations   

    Returns:
    - float: The reward value for the miner.
    """
    print("*************************************************")
    print(response)
    
    bt.logging.info(
        f"Miner reward: {response}"
    )
    
    #time.sleep(10)

    score = 0
 
    if len(response.results) == num_recs:
        score = 0.01
    elif len(response.results) != 0:
        score = 0.001
    
    bt.logging.info(
        f"Miner reward score: {score}, response val: {response}"
    )
    return score    
    


def get_rewards(
    self,
    num_recs: int,
    responses: List[BitrecsRequest],   
) -> np.ndarray:
    """
    Returns an array of rewards for the given query and responses.

    Args:
    - query (int): The query sent to the miner.
    - responses (List[float]): A list of responses from the miner.

    Returns:
    - np.ndarray: An array of rewards for the given query and responses.
    """
    # Get all the reward results by iteratively calling your reward() function.
    
    return np.array([reward(num_recs, response) for response in responses])
