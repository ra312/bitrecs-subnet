#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Store the terminal size
TERM_LINES=$(tput lines)
TERM_COLS=$(tput cols)

# Clear screen and hide cursor
clear
tput civis

# Function to position cursor
position_cursor() {
    tput cup $1 $2
}

# Function to draw logo at specific position
draw_logo() {
    local start_line=$1
    position_cursor $start_line 0
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
}

# Function to draw progress bar
draw_progress_bar() {
    local progress=$1
    local bar_size=50
    local filled=$(($progress * $bar_size / 100))
    local empty=$((bar_size - filled))
    
    position_cursor $((TERM_LINES-2)) 0
    echo -ne "${YELLOW}Progress: ["
    for ((i=0; i<filled; i++)); do echo -ne "▇"; done
    for ((i=0; i<empty; i++)); do echo -ne " "; done
    echo -ne "] ${progress}%${NC}"
}

# Function to update log area
update_log() {
    local message=$1
    local log_start=$((12))  # Start after logo
    local log_end=$((TERM_LINES-3))  # End before progress bar
    
    # Store current cursor position
    local current_line=$(tput lines)
    local current_col=$(tput cols)
    
    # Move to log area and print message
    position_cursor $log_start 0
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
    
    # Return cursor to original position
    position_cursor $current_line $current_col
}

# Error handling
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'if [ $? -ne 0 ]; then update_log "${RED}ERROR: Command \"${last_command}\" failed${NC}"; exit 1; fi' EXIT

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Initial setup
clear
draw_logo 0
draw_progress_bar 0

# 1. Networking Setup
update_log "Setting up networking..."
apt install ufw -y &> >(while read line; do update_log "$line"; done)
apt-get update && apt-get upgrade -y &> >(while read line; do update_log "$line"; done)
ufw allow 22 &> >(while read line; do update_log "$line"; done)
ufw allow proto tcp to 0.0.0.0/0 port 8091 &> >(while read line; do update_log "$line"; done)
yes | ufw enable &> >(while read line; do update_log "$line"; done)
ufw reload &> >(while read line; do update_log "$line"; done)
draw_progress_bar 20
update_log "Network setup completed"

# 2. Server Setup
update_log "Configuring server..."
mount -o remount,size=8G /tmp &> >(while read line; do update_log "$line"; done)
apt-get update && apt-get upgrade -y &> >(while read line; do update_log "$line"; done)
apt install python3-pip -y &> >(while read line; do update_log "$line"; done)
apt install python3.12-venv -y &> >(while read line; do update_log "$line"; done)
draw_progress_bar 40
update_log "Server setup completed"

# 3. Create Working Directory
update_log "Creating working directory..."
mkdir -p /bt &> >(while read line; do update_log "$line"; done)
cd /bt
draw_progress_bar 50
update_log "Working directory created"

# 4. Python Environment Setup
update_log "Setting up Python environment..."
python3.12 -m venv bt_venv &> >(while read line; do update_log "$line"; done)
source bt_venv/bin/activate
pip3 install bittensor[torch] &> >(while read line; do update_log "$line"; done)
echo "source /bt/bt_venv/bin/activate" >> ~/.bashrc
draw_progress_bar 75
update_log "Python environment setup completed"

# 5. Miner Installation
update_log "Installing miner..."
cd /bt
if [ -d "bitrecs-subnet" ]; then
    rm -rf bitrecs-subnet
fi
git clone https://github.com/janusdotai/bitrecs-subnet.git &> >(while read line; do update_log "$line"; done)
cd bitrecs-subnet
pip3 install -r requirements.txt &> >(while read line; do update_log "$line"; done)
python3 -m pip install -e . &> >(while read line; do update_log "$line"; done)
draw_progress_bar 100
update_log "Miner installation completed"

# Show completion message
position_cursor $((TERM_LINES-5)) 0
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       Installation Complete! 🚀         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

# Show cursor again
tput cnorm

update_log "Your Bitrecs miner has been successfully installed!"
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Configure your wallet if you haven't already"
echo -e "2. Start the miner with your preferred configuration\n"cho -e "2. Start the miner with your preferred configuration\n"
