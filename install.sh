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

# Function to clear specific area of screen
clear_area() {
    local start_line=$1
    local end_line=$2
    for ((i=start_line; i<=end_line; i++)); do
        tput cup $i 0
        tput el
    done
}

# Function to position cursor
position_cursor() {
    tput cup $1 $2
}

# Create temp file for logs
TMPFILE=$(mktemp)
# Clean up temp file on exit
trap 'rm -f $TMPFILE' EXIT

# Function to draw logo
draw_logo() {
    position_cursor 0 0
    echo -ne "${BLUE}"
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
    echo -ne "${NC}"
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

# Function to update display
update_display() {
    local message=$1
    local progress=$2
    
    # Save cursor position
    tput sc
    
    # Clear and redraw logo
    clear_area 0 10
    draw_logo
    
    # Draw progress bar
    draw_progress_bar $progress
    
    # Update log area (between logo and progress bar)
    position_cursor 12 0
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
    
    # Show last few lines of log file
    position_cursor 13 0
    tail -n $((TERM_LINES-16)) $TMPFILE
    
    # Restore cursor position
    tput rc
}

# Initialize screen
clear
tput civis  # Hide cursor
draw_logo
draw_progress_bar 0

# Main installation process
echo "Starting installation..." > $TMPFILE

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# 1. Networking Setup
{
    update_display "Setting up networking..." 5
    apt install ufw -y 2>&1 | tee -a $TMPFILE
    update_display "Updating system..." 10
    apt-get update && apt-get upgrade -y 2>&1 | tee -a $TMPFILE
    update_display "Configuring firewall..." 15
    ufw allow 22 2>&1 | tee -a $TMPFILE
    ufw allow proto tcp to 0.0.0.0/0 port 8091 2>&1 | tee -a $TMPFILE
    yes | ufw enable 2>&1 | tee -a $TMPFILE
    ufw reload 2>&1 | tee -a $TMPFILE
    update_display "Network setup completed" 20
} 

# 2. Server Setup
{
    update_display "Configuring server..." 25
    mount -o remount,size=8G /tmp 2>&1 | tee -a $TMPFILE
    update_display "Updating packages..." 30
    apt-get update && apt-get upgrade -y 2>&1 | tee -a $TMPFILE
    update_display "Installing Python..." 35
    apt install python3-pip -y 2>&1 | tee -a $TMPFILE
    apt install python3.12-venv -y 2>&1 | tee -a $TMPFILE
    update_display "Server setup completed" 40
}

# 3. Create Working Directory
{
    update_display "Creating working directory..." 45
    mkdir -p /bt 2>&1 | tee -a $TMPFILE
    cd /bt
    update_display "Working directory created" 50
}

# 4. Python Environment Setup
{
    update_display "Setting up Python environment..." 55
    python3.12 -m venv bt_venv 2>&1 | tee -a $TMPFILE
    source bt_venv/bin/activate
    update_display "Installing bittensor..." 60
    pip3 install bittensor[torch] 2>&1 | tee -a $TMPFILE
    echo "source /bt/bt_venv/bin/activate" >> ~/.bashrc
    update_display "Python environment setup completed" 75
}

# 5. Miner Installation
{
    update_display "Installing miner..." 80
    cd /bt
    if [ -d "bitrecs-subnet" ]; then
        rm -rf bitrecs-subnet
    fi
    update_display "Cloning repository..." 85
    git clone https://github.com/janusdotai/bitrecs-subnet.git 2>&1 | tee -a $TMPFILE
    cd bitrecs-subnet
    update_display "Installing dependencies..." 90
    pip3 install -r requirements.txt 2>&1 | tee -a $TMPFILE
    python3 -m pip install -e . 2>&1 | tee -a $TMPFILE
    update_display "Miner installation completed" 100
}

# Show completion message
position_cursor $((TERM_LINES-5)) 0
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       Installation Complete! 🚀         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

# Show cursor again and cleanup
tput cnorm

update_display "Your Bitrecs miner has been successfully installed!" 100
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Configure your wallet if you haven't already"
echo -e "2. Start the miner with your preferred configuration\n"cho -e "2. Start the miner with your preferred configuration\n"cho -e "2. Start the miner with your preferred configuration\n"
