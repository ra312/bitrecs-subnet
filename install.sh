#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${BLUE}"
cat << "EOF"
 ▄▄▄▄    ██▓▄▄▄█████▓ ██▀███  ▓█████  ▄████▄    ██████ 
▓█████▄ ▓██▒▓  ██▒ ▓▒▓██ ▒ ██▒▓█   ▀ ▒██▀ ▀█  ▒██    ▒ 
▒██▒ ▄██▒██▒▒ ▓██░ ▒░▓██ ░▄█ ▒▒███   ▒▓█    ▄ ░ ▓██▄   
▒██░█▀  ░██░░ ▓██▓ ░ ▒██▀▀█▄  ▒▓█  ▄ ▒▓▓▄ ▄██▒  ▒   ██▒
░▓█  ▀█▓░██░  ▒██▒ ░ ░██▓ ▒██▒░▒████▒▒ ▓███▀ ░▒██████▒▒
░▒▓███▀▒░▓    ▒ ░░   ░ ▒▓ ░▒▓░░░ ▒░ ░░ ░▒ ▒  ░▒ ▒▓▒ ▒ ░
▒░▒   ░  ▒ ░    ░      ░▒ ░ ▒░ ░ ░  ░  ░  ▒   ░ ░▒  ░ ░
 ░    ░  ▒ ░  ░        ░░   ░    ░   ░        ░  ░  ░  
 ░       ░              ░        ░  ░ ░ ░            ░  
      ░                                ░                 
EOF
echo -e "${NC}"

# Progress bar function
progress() {
    local duration=$1
    local step=$((duration/50))
    local progress=0
    local increment=$((100/50))
    
    echo -ne "${YELLOW}Progress: |"
    while [ $progress -le 100 ]
    do
        echo -ne "▇"
        sleep $step
        progress=$((progress + increment))
    done
    echo -e "| ${progress}% ${NC}"
}

# Verbose logging function
log() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ${1}${NC}"
}

# Error handling
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'if [ $? -ne 0 ]; then echo -e "${RED}ERROR: Command \"${last_command}\" failed${NC}"; fi' EXIT

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# 1. Networking Setup
log "Setting up networking..."
apt install ufw -y
apt-get update && apt-get upgrade -y
ufw allow 22
ufw allow proto tcp to 0.0.0.0/0 port 8091
yes | ufw enable
ufw reload
progress 2
log "Network setup completed"

# 2. Server Setup
log "Configuring server..."
mount -o remount,size=8G /tmp
apt-get update && apt-get upgrade -y
apt install python3-pip -y
apt install python3.12-venv -y
progress 3
log "Server setup completed"

# 3. Create Working Directory
log "Creating working directory..."
mkdir -p /bt
cd /bt
progress 1
log "Working directory created"

# 4. Python Environment Setup
log "Setting up Python environment..."
python3.12 -m venv bt_venv
source bt_venv/bin/activate
pip3 install bittensor[torch]
echo "source /bt/bt_venv/bin/activate" >> ~/.bashrc
progress 5
log "Python environment setup completed"

# 5. Miner Installation
log "Installing miner..."
cd /bt
if [ -d "bitrecs-subnet" ]; then
    rm -rf bitrecs-subnet
fi
git clone https://github.com/janusdotai/bitrecs-subnet.git
cd bitrecs-subnet
pip3 install -r requirements.txt
python3 -m pip install -e .
progress 4
log "Miner installation completed"

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       Installation Complete! 🚀         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

log "Your Bitrecs miner has been successfully installed!"
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Configure your wallet if you haven't already"
echo -e "2. Start the miner with your preferred configuration\n"
