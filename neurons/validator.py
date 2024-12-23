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


from datetime import timedelta
import time
import bittensor as bt
import asyncio
from template.base.validator import BaseValidatorNeuron
from template.utils.runtime import execute_periodically
from template.utils.version import LocalMetadata
from template.validator import forward
from template.protocol import BitrecsRequest
from template.utils.gpu import GPUInfo
from template.utils import constants as CONST
from dotenv import load_dotenv
load_dotenv()


class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()
        self.total_request_in_interval = 0


    async def forward(self, pr : BitrecsRequest = None):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Selecting a top candidate from the responses
        - Return top candidate to the client
        - Rewarding the miners
        - Updating the scores
        """                
        return await forward(self, pr)
    
    
    @execute_periodically(timedelta(seconds=CONST.VERSION_CHECK_INTERVAL))
    async def version_sync(self):
        bt.logging.trace(f"Version sync ran at {int(time.time())}")
        try:
            self.local_metadata = LocalMetadata.local_metadata()
            self.local_metadata.uid = self.uid
            self.local_metadata.hotkey = self.wallet.hotkey.ss58_address
            local_head = self.local_metadata.head
            remote_head = self.local_metadata.remote_head
            code_version = self.local_metadata.version
            bt.logging.info(f"Bitrecs Version:\033[32m {code_version}\033[0m")
            if local_head != remote_head:
                bt.logging.info(f"Head:\033[33m {local_head}\033[0m / Remote: \033[33m{remote_head}\033[0m")                
                bt.logging.warning(f"{self.neuron_type} version mismatch: Please update your code to the latest version.")
            else:
                 bt.logging.info(f"Head:\033[32m {local_head}\033[0m / Remote: \033[32m{remote_head}\033[0m")
        except Exception as e:
            bt.logging.error(f"Failed to get version with exception: {e}")
        return
    

async def main():     
    await GPUInfo.log_gpu_info()
    with Validator() as validator:
        start_time = time.time()        
        while True:
            await validator.version_sync()
            bt.logging.info(f"Validator {validator.uid} running... {int(time.time())}")
            if time.time() - start_time > 300:
                bt.logging.info(
                    f"---Total request in last 5 minutes: {validator.total_request_in_interval}"
                )
                start_time = time.time()
                validator.total_request_in_interval = 0
            await asyncio.sleep(15)

if __name__ == "__main__": 
    asyncio.run(main())
