# Deezy Betting Bot

A simple Discord bot that allows users to create and participate in custom bets. The bot provides functionality for defining bets with default or custom options, tracking participants' choices, and declaring winners. It also stores data persistently, so active bets and user statistics remain intact across bot restarts.

## Features

- **Create Bets**: Users can start bets with default "Over/Under" options or define custom betting options.
- **Interactive Betting**: Users interact with the bot by selecting their choice through buttons.
- **Declare Results**: Admins or the creator of a bet can declare the winner, and the bot announces who won.
- **Track Wins and Losses**: The bot tracks wins and losses for each user.
- **Persistent Storage**: Bets and user stats are stored in JSON files, ensuring that data persists across bot restarts.
- **Simple Commands**: Easily manage bets and user stats with intuitive commands.

## Requirements

- Python 3.8+
- `discord.py` library
- A Discord bot token (you can get this from the [Discord Developer Portal](https://discord.com/developers/applications))

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/tidnaaB/discord-betting-bot.git
cd discord-betting-bot
```

### 2. Install Dependencies

Make sure you have `discord.py` installed. You can install it with the following:

```bash
pip install discord.py
```

### 3. Set Up Your Bot Token

Create a `.env` file and add your bot token:

```env
DISCORD_TOKEN=your-bot-token-here
```

Alternatively, you can directly insert your bot token in the `bot.run()` line in the script (not recommended for production).

### 4. Run the Bot

Run the bot with Python:

```bash
python betting_bot.py
```

Once the bot is running, invite it to your Discord server and start creating bets!

## Commands

### 1. **`!bet`**

- Create a new bet with default or custom options.
- **Usage**:
  - `!bet "Bet Name"` (default options: Over/Under)
  - `!bet "Bet Name" "Yes" "No"` (custom options)

### 2. **`!winner`**

- Declare the winner of a bet.
- **Usage**: `!winner <bet_id> <winning_option>`
- Example: `!winner 1 1` (declares option 1 as the winner)

### 3. **`!bets`**

- View all active bets.
- **Usage**: `!bets`

### 4. **`!stats`**

- View your or another user's stats (wins/losses).
- **Usage**: `!stats [@user]`
- Example: `!stats @JohnDoe`

### 5. **`!dbet`**

- Delete a bet by its ID.
- **Usage**: `!dbet <bet_id>`
- Example: `!dbet 1` (deletes the bet with ID 1)

## Example Workflow

1. **Create a bet**:

   - `!bet "Will it rain?"`
2. **Users interact**: Users select their choices via buttons, such as "Over" or "Under."
3. **Declare the winner**:

   - The bet creator/admin declares the winner using `!winner <bet_id> <option>`.
4. **View bets**: Check active bets with `!bets`.
5. **Check stats**: View your wins and losses with `!stats`.

## Persistent Storage

The bot stores active bets and user statistics in JSON files (`active_bets.json` and `user_stats.json`). This ensures that all bet data and stats are preserved across bot restarts.

## Contributing

Feel free to contribute by opening issues or submitting pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
