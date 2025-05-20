#!/bin/bash

# Default to production environment
ENV="mainnet"
NETUID=60
NETWORK="finney"

if [ "$1" == "--test" ]; then
    ENV="testnet"
    NETUID=350
    NETWORK="test"
fi

echo "Starting validator in $ENV environment with netuid $NETUID"
python -m neurons.validator --netuid $NETUID \
    --subtensor.chain_endpoint $NETWORK --subtensor.network $NETWORK \
    --wallet.name validator --wallet.hotkey default \
    --axon.port 8091 --axon.external_port 8091 \
    --logging.debug
