#!/bin/bash

# Default to production miner environment
ENV="mainnet"
TASK=""
WALLET_SUFFIX=".mainnet"
NETUID=60
NETWORK="finney"
PORT=8090  # Default port

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        validator)
            TASK="validator"
            shift
            ;;
        miner)
            TASK="miner"
            shift
            ;;
        --test|--testnet)
            ENV="testnet"
            WALLET_SUFFIX=""
            NETUID=350
            NETWORK="test"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

if [ -z "$TASK" ]; then
    echo "Please specify a task: validator, miner"
    exit 1
fi

echo "Starting $TASK in $ENV environment with netuid $NETUID on port $PORT"

echo "Activating virtual environment"
source venv/bin/activate

venv/bin/python3 -m neurons.$TASK --netuid $NETUID \
    --subtensor.chain_endpoint $NETWORK --subtensor.network $NETWORK \
    --wallet.name $TASK$WALLET_SUFFIX --wallet.hotkey default \
    --axon.port $PORT --axon.external_port $PORT \
    --logging.debug