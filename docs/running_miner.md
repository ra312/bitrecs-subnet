# Running a Miner Node

## Hardware Requirements

- RTX3090
- 16GB RAM
- 50GB SSD
- Low latency internet connection

## Software Requirements

- Python 3.12
- Bittensor wallet coldkey + hotkey
- .env example if you want to use our base miner class with an LLM provider

## Running the Miner

Start your miner using the following command:

```bash
pm2 start neurons/miner.py \
    --netuid 60 \
    --subtensor.network <finney/local/test> \
    --wallet.name <your coldkey> \
    --wallet.hotkey <your hotkey> \
    --logging.trace
```