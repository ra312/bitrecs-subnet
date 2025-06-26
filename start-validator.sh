#!/bin/bash

# Default to production environment
ENV="mainnet"
NETUID=60
NETWORK="finney"
PORT=8090  # Default port
PROXY_PORT=10913 # Used on DigitalOcean

if [[ "$@" == *"--test"* || "$@" == *"--testnet"* ]]; then
    ENV="testnet"
    NETUID=350
    NETWORK="test"
fi

#if proxy.port in args anywhere, use it
if [[ "$@" == *"--proxy.port"* ]]; then
    PROXY_PORT=$(echo "$@" | grep -o -- "--proxy.port [0-9]*" | grep -o "[0-9]*")
fi

# Activate virtual environment
echo "Activating virtual environment"
source venv/bin/activate

echo "Starting validator in $ENV environment with netuid $NETUID on port $PORT and proxy port $PROXY_PORT"
venv/bin/python3 -m neurons.validator --netuid $NETUID \
    --subtensor.chain_endpoint $NETWORK --subtensor.network $NETWORK \
    --wallet.name validator --wallet.hotkey default \
    --axon.port $PORT --axon.external_port $PORT \
    --logging.debug --proxy.port $PROXY_PORT