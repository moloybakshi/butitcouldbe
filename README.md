# Convince the AI! Game

A fun debate game where you try to convince an AI character about various scenarios using the Gemma 3:4b model.

## Requirements

- macOS
- Python 3
- pip3
- Internet connection (for initial setup)

## Installation

1. Download or clone this repository
2. Open Terminal and navigate to the game directory
3. Make the installer executable:
   ```bash
   chmod +x install.sh
   ```
4. Run the installer:
   ```bash
   ./install.sh
   ```

The installer will:
- Check for and install Ollama if needed
- Download the Gemma 3:4b model
- Install required Python packages
- Set up the game files

## Running the Game

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```
2. Start the game:
   ```bash
   python3 game.py
   ```

## How to Play

1. Choose whether to convince the AI that a scenario is TRUE or FALSE
2. Type your arguments in the input box
3. Press Enter to send your message
4. The AI will respond and show its conviction level
5. Try to convince the AI before running out of responses!

## Features

- Dynamic AI responses using Gemma 3:4b
- Visual conviction meter
- Automated responses option
- Conversation saving
- Unique scenarios for each game

## Troubleshooting

If you encounter any issues:

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```
2. Check your Python version:
   ```bash
   python3 --version
   ```
3. Verify the Gemma model is installed:
   ```bash
   ollama list
   ```

## License

This project is open source and available under the MIT License.