# Update and install dependencies
apt update && apt install -y software-properties-common curl

# Add deadsnakes PPA for newer Python versions
add-apt-repository ppa:deadsnakes/ppa -y
apt update

# Install Python 3.11 and pip
apt install -y python3.11 python3.11-venv python3.11-distutils

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Verify versions
python3.11 --version
pip3.11 --version

# Install uv (fast Python package manager)
curl -Ls https://astral.sh/uv/install.sh | bash

# Add uv to path (assuming default install location)
export PATH="$HOME/.cargo/bin:$PATH"
uv --version

# Create and activate virtual environment using uv + Python 3.11
uv venv .venv --python python3.11
source .venv/bin/activate
uv pip install bittensor-cli
echo "please save your machine's public ssh key to the github account"

git clone git clone git@github.com:Bitsec-AI/subnet.git

cd subnet

uv pip install -r requirements.txt


