# Running a Validator Node

## Hardware Requirements

- RTX3090
- 32GB RAM
- 200GB SSD
- Low latency internet connection

## Software Requirements

- Ubuntu or linux distro
- Python 3.12
- Create a wandb account and login on your machine via pip
- Bittensor wallet coldkey + hotkey
- Fill out .env example

## Running the Validator

Start your validator using the following command:

```bash
pm2 start python neurons/validator.py \
    --netuid 1 \
    --subtensor.network <finney/local/test> \
    --wallet.name validator \
    --wallet.hotkey default \
    --logging.trace \
    --api.enabled \
    --api.exclusive \
    --wandb.project_name template-validator-mainnet \
    --wandb.entity bitrecs
```