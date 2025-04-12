#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Convince the AI! Game Installation...${NC}"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This installer is for macOS only.${NC}"
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is required but not installed.${NC}"
    exit 1
fi

# Check for virtualenv
if ! command -v virtualenv &> /dev/null; then
    echo -e "${YELLOW}Installing virtualenv...${NC}"
    pip3 install virtualenv
fi

# Create and activate virtual environment
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Ollama not found. Installing Ollama...${NC}"

    # Download and install Ollama
    curl -fsSL https://ollama.com/install.sh | sh

    # Start Ollama service
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    ollama serve &
    sleep 5  # Wait for service to start
else
    echo -e "${GREEN}Ollama is already installed.${NC}"

    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${YELLOW}Starting Ollama service...${NC}"
        ollama serve &
        sleep 5
    fi
fi

# Check for Gemma model
echo -e "${YELLOW}Checking for Gemma model...${NC}"
if ! curl -s http://localhost:11434/api/tags | grep -q "gemma3:4b"; then
    echo -e "${YELLOW}Downloading Gemma model (this may take a while)...${NC}"
    ollama pull gemma3:4b
else
    echo -e "${GREEN}Gemma model is already installed.${NC}"
fi

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Create assets directory if it doesn't exist
if [ ! -d "assets/sprites" ]; then
    echo -e "${YELLOW}Creating assets directory...${NC}"
    mkdir -p assets/sprites
fi

# Make the game executable
echo -e "${YELLOW}Setting up the game...${NC}"
chmod +x game.py

# Create a launcher script
echo '#!/bin/bash
source venv/bin/activate
python3 game.py' > start_game.sh
chmod +x start_game.sh

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}To start the game, run:${NC}"
echo -e "./start_game.sh"
echo -e "\n${YELLOW}Note: Make sure Ollama is running before starting the game.${NC}"
echo -e "You can start Ollama with: ollama serve"