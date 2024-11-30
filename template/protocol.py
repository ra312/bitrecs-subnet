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

import bittensor as bt
import pydantic
from typing import List

class BitrecsRequest(bt.Synapse):
    created_at: str | None
    user: str | None
    num_results: int = pydantic.Field(
        0,
        description="Expected number of recs",
    )
    query: str | None
    context: str | None
    site_key: str | None
    results: List[str] | None
    models_used: List[str] | None
    miner_uid: str | None
    miner_hotkey: str | None

    # def deserialize(self) -> "BitrecsRequest":
    #     return self    
    
    # def deserialize(self) -> dict:
    #     return {
    #         "created_at": self.created_at,
    #         "user": self.user,
    #         "num_results": self.num_results,
    #         "query": self.query,
    #         "context": self.context,
    #         "site_key": self.site_key,
    #         "results": self.results,
    #         "models_used": self.models_used,
    #         "miner_uid": self.miner_uid,
    #         "miner_hotkey": self.miner_hotkey,
    #     }



# class ProductRecResponse:
#     user: str
#     original_query: str    
#     status_code: int
#     status_text: str
#     response_text: str
#     created_at: str
#     results: List[str]
#     models_used: List[str]
#     catalog_size: int
#     miner_uid: str
#     miner_public_key: str
#     reasoning: str