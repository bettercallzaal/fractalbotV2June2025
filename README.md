# ZAO Fractal Voting System

A Discord bot that facilitates structured group voting with a progressive level system, designed to enhance group decision making through a fractal voting process.

## Overview

The ZAO Fractal Voting System is a Discord bot that organizes structured voting with these core features:

- **Progressive Level-Based Voting**: Members vote through levels 6→1, with winners at each level
- **Public & Transparent Voting**: All votes are publicly announced in chat so everyone sees who voted for whom
- **Dynamic Vote Management**: Users can change their votes at any time during each round
- **Winner Announcements**: Clear visual announcements for level winners and final results
- **Multi-Group Support**: Multiple fractal groups can operate simultaneously

## Features

- Create fractal voting groups directly from voice channels
- Private threads for each voting group
- Intuitive UI with colored voting buttons
- Real-time vote tracking and announcements
- Complete results visualization at the end of the process
- Support for groups of 2-6 members

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/bettercallzaal/fractalbotV2June2025.git
   cd fractalbotV2June2025
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the `config` directory using the template:
   ```
   cp config/.env.template config/.env
   ```

4. Edit the `.env` file and add your Discord bot token and other configuration

5. Run the bot:
   ```
   python main.py
   ```

## Usage

### Bot Commands

- `/zaofractal` - Create a new fractal voting group from your current voice channel
- `/status` - Show the current status of an active fractal group
- `/endgroup` - End an active fractal group (facilitator only)

### Voting Process

1. Join a voice channel with 2-6 members
2. Use the `/zaofractal` command in a text channel
3. Enter a name for your fractal group
4. A private thread will be created with all voice members added
5. Vote by clicking on the buttons with candidate names
6. Votes require 50% or more to win a level
7. After a winner is determined, the next level begins
8. Process continues until all levels are complete

## Project Structure

```
ZAO-FRACTAL-BOT/
├── main.py                  # Bot entry point
├── config/
│   ├── config.py            # Configuration parameters
│   └── .env                 # Environment variables (tokens)
├── cogs/
│   ├── base.py              # Base cog with utility methods
│   └── fractal/
│       ├── __init__.py      # Package initialization
│       ├── cog.py           # Command handlers
│       ├── group.py         # FractalGroup core logic
│       └── views.py         # UI components
└── utils/
    └── logging.py           # Logging configuration
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT License - see the LICENSE file for details.
