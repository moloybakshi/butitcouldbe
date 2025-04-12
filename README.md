# Convince the AI Game

A fun interactive game where you try to convince an AI character about various scenarios using the Ollama Gemma 3:4b model.

## Prerequisites

1. Python 3.7 or higher
2. Ollama installed and running locally
3. Gemma 3:4b model pulled in Ollama

## Installation

1. Install the required Python packages:
```bash
pip install -r requirements.txt
```

2. Make sure Ollama is running locally and you have pulled the Gemma 3:4b model:
```bash
ollama pull gemma:3b
```

## How to Play

1. Run the game:
```bash
python game.py
```

2. Game Instructions:
- A random scenario will be presented at the top of the screen
- Type your arguments in the input box at the bottom
- Press Enter to submit your argument
- The AI will respond and show its level of conviction
- Try to convince the AI by providing compelling arguments
- The game ends when the AI is fully convinced (conviction meter reaches 100%)
- Press 'R' to restart with a new scenario

## Features

- Interactive text input
- Real-time AI responses using Ollama
- Visual conviction meter
- Multiple random scenarios
- Simple and intuitive interface

## Note

Make sure Ollama is running on your local machine (default port 11434) before starting the game.