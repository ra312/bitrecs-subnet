# The MIT License (MIT)
# Copyright © 2021 Yuma Rao
# Copyright © 2023 Opentensor Foundation
# Copyright © 2023 Opentensor Technologies Inc

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

import bittensor as bt
from typing import List, Optional, Union, Any, Dict
from template.protocol import Dummy
from bittensor.utils.subnets import SubnetsAPI
from template.protocol import BitrecsRequest, BitrecsResponse

class DummyAPI(SubnetsAPI):
    def __init__(self, wallet: "bt.wallet"):
        super().__init__(wallet)
        self.netuid = 33
        self.name = "dummy"

    def prepare_synapse(self, dummy_input: int) -> Dummy:
        synapse.dummy_input = dummy_input
        return synapse

    def process_responses(
        self, responses: List[Union["bt.Synapse", Any]]
    ) -> List[int]:
        outputs = []
        for response in responses:
            if response.dendrite.status_code != 200:
                continue
            return outputs.append(response.dummy_output)
        return outputs



# class BitrecsAPI(SubnetsAPI):
#     def __init__(self, wallet: "bt.wallet"):
#         super().__init__(wallet)
#         self.netuid = 1
#         self.name = "bitrecsapi"

#     def prepare_synapse(self, br_rec: BitrecsRequest) -> BitrecsRequest:
#         br_rec.user = "Bitrecs API Request"        
#         return br_rec

#     def process_responses(
#         self, responses: List[Union["bt.Synapse", Any]]
#     ) -> List[int]:
#         outputs = []
#         for response in responses:
#             if response.dendrite.status_code != 200:
#                 continue
#             #return outputs.append(response.dummy_output)
#             return outputs.append(response)
#         return outputs


# import bittensor
# # Define your custom synapse class
# class MySynapse( bittensor.Synapse ):
#     input: int = 1
#     output: int = None

# # Define a custom request forwarding function using your synapse class
# def forward( synapse: MySynapse ) -> MySynapse:
#     # Apply custom logic to synapse and return it
#     synapse.output = 2
#     return synapse

# # Define a custom request verification function
# def verify_my_synapse( synapse: MySynapse ):
#     # Apply custom verification logic to synapse
#     # Optionally raise Exception
#     assert synapse.input == 1
#     ...

# # Define a custom request blacklist function
# def blacklist_my_synapse( synapse: MySynapse ) -> bool:
#     # Apply custom blacklist
#     return False ( if non blacklisted ) or True ( if blacklisted )

# # Define a custom request priority function
# def prioritize_my_synapse( synapse: MySynapse ) -> float:
#     # Apply custom priority
#     return 1.0

# # Initialize Axon object with a custom configuration
# my_axon = bittensor.Axon(
#     config=my_config,
#     wallet=my_wallet,
#     port=9090,
#     ip="192.0.2.0",
#     external_ip="203.0.113.0",
#     external_port=7070
# )

# # Attach the endpoint with the specified verification and forward functions.
# my_axon.attach(
#     forward_fn = forward_my_synapse,
#     verify_fn = verify_my_synapse,
#     blacklist_fn = blacklist_my_synapse,
#     priority_fn = prioritize_my_synapse
# )

# # Serve and start your axon.
# my_axon.serve(
#     netuid = ...
#     subtensor = ...
# ).start()

# # If you have multiple forwarding functions, you can chain attach them.
# my_axon.attach(
#     forward_fn = forward_my_synapse,
#     verify_fn = verify_my_synapse,
#     blacklist_fn = blacklist_my_synapse,
#     priority_fn = prioritize_my_synapse
# ).attach(
#     forward_fn = forward_my_synapse_2,
#     verify_fn = verify_my_synapse_2,
#     blacklist_fn = blacklist_my_synapse_2,
#     priority_fn = prioritize_my_synapse_2
# ).serve(
#     netuid = ...
#     subtensor = ...
# ).start()