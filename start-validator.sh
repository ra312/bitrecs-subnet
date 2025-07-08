#!/bin/bash

# Default to production environment
ENV="mainnet"
# NETUID=60
# NETWORK="finney"
# PORT=8090  # Default port

NETUID="$1"
PORT="$2"
WALLET_HOTKEY_NAME="$3"
WALLET_COLDKEY_NAME="$4"


PROXY_PORT=10913 # Used on DigitalOcean
COMMAND_WITH_PATH="python3"


#if proxy.port in args anywhere, use it
if [[ "$@" == *"--proxy.port"* ]]; then
    PROXY_PORT=$(echo "$@" | grep -o -- "--proxy.port [0-9]*" | grep -o "[0-9]*")
fi

# Activate virtual environment if it exists
if [[ -d "venv" && -f "venv/bin/activate" ]]; then
    echo "Activating virtual environment"
    source venv/bin/activate
    COMMAND_WITH_PATH="venv/bin/python3"
fi

echo "Starting validator in $ENV environment with netuid $NETUID on port $PORT and proxy port $PROXY_PORT"
$COMMAND_WITH_PATH -m neurons.validator --netuid $NETUID \
    --subtensor.chain_endpoint $NETWORK --subtensor.network $NETWORK \
    --wallet.name validator --wallet.hotkey default \
    --axon.port $PORT --axon.external_port $PORT \
    --logging.debug --proxy.port $PROXY_PORT

# Build command to run via PM2
VALIDATOR_COMMAND="$COMMAND_WITH_PATH -m neurons.miner --netuid $NETUID \
    --subtensor.chain_endpoint $NETWORK --subtensor.network $NETWORK \
    --wallet.name $WALLET_COLDKEY_NAME --wallet.hotkey $WALLET_HOTKEY_NAME \
    --axon.port $PORT --axon.external_port $PORT \
    --logging.debug --proxy.port $PROXY_PORT"

pm2_name="validator-$NETUID"
pm2 delete $pm2_name  && pm2 start "$VALIDATOR_COMMAND"  --name $pm2_name   && pm2 logs $pm2_name
