import json
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import View, Button

# Load .env and set DISCORD_TOKEN
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# File paths for storing stats and active bets
STATS_FILE = "user_stats.json"
BETS_FILE = "active_bets.json"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!", intents=intents
)  # Customize the command prefix as needed


# Load stats from JSON file
def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(
                f"Warning: {STATS_FILE} is empty or invalid. Initializing empty stats."
            )
            return {}
    else:
        return {}


# Save stats to JSON file
def save_stats(user_stats):
    with open(STATS_FILE, "w") as file:
        json.dump(user_stats, file, indent=4)


# Load active bets from JSON file
def load_bets():
    if os.path.exists(BETS_FILE):
        try:
            with open(BETS_FILE, "r") as file:
                active_bets = json.load(file)
                for bet_id, bet in active_bets.items():
                    if "options" not in bet or not isinstance(bet["options"], dict):
                        active_bets[bet_id]["options"] = {
                            1: "Over",
                            2: "Under",
                        }  # Default options
                    else:
                        # Ensure both keys 1 and 2 exist in the options
                        if 1 not in bet["options"] or 2 not in bet["options"]:
                            active_bets[bet_id]["options"] = {
                                1: "Over",
                                2: "Under",
                            }  # Reset to default if incomplete
                return {int(k): v for k, v in active_bets.items()}
        except json.JSONDecodeError:
            print(f"Warning: {BETS_FILE} is empty or invalid. Initializing empty bets.")
            return {}
    else:
        return {}


# Save active bets to JSON file
def save_bets(active_bets):
    with open(BETS_FILE, "w") as file:
        json.dump(active_bets, file, indent=4)


# Load stats and active bets on bot startup
@bot.event
async def on_ready():
    global user_stats, active_bets
    user_stats = load_stats()
    active_bets = load_bets()
    print(f"Logged in as {bot.user}")


# Class to handle custom bet buttons (with dynamic options)
class CustomBetButtons(View):
    def __init__(self, bet_id, options):
        super().__init__()
        self.bet_id = bet_id

        # Add buttons for options 1 and 2
        self.add_item(
            Button(
                label=f"{options[1]}", style=discord.ButtonStyle.green, custom_id="1"
            )
        )
        self.add_item(
            Button(label=f"{options[2]}", style=discord.ButtonStyle.red, custom_id="2")
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        user_name = interaction.user.name
        bet_id = self.bet_id
        option = interaction.data["custom_id"]  # This will be "1" or "2"

        # Save the user's choice directly into the active_bets for this bet
        if bet_id in active_bets:
            if "user_choices" not in active_bets[bet_id]:
                active_bets[bet_id]["user_choices"] = {}
            active_bets[bet_id]["user_choices"][user_name] = option

            # Save the updated active_bets with the user choice
            save_bets(active_bets)

        await interaction.response.send_message(
            f"{interaction.user.name} chose option {option}!", ephemeral=True
        )
        return True


# Command to create a bet with options (defaults to Over/Under)
@bot.command(name="bet")
async def bet(ctx, bet_name: str, *custom_options):
    if not custom_options:
        options = {1: "Over", 2: "Under"}
    else:
        if len(custom_options) >= 2:
            options = {1: custom_options[0], 2: custom_options[1]}
        else:
            await ctx.send(
                "Please provide exactly two custom options or none to use the default Over/Under options."
            )
            return

    # Create a bet dictionary for the bet details
    bet_id = len(active_bets) + 1
    active_bets[bet_id] = {
        "creator": ctx.author.name,
        "bet_name": bet_name,
        "options": options,
        "winner": None,
        "user_choices": {},
    }

    # Save the active bets
    save_bets(active_bets)

    # Embed message structure for neat display
    embed = discord.Embed(
        title=f"**Bet**: {bet_name}",
        description=f"**Creator**: {ctx.author.name} | **ID**: {bet_id}",
        color=discord.Color.blue(),
    )

    # Send the embed and add buttons with custom colors
    view = CustomBetButtons(bet_id, options)
    await ctx.send(embed=embed, view=view)


# Command to declare a result for a bet (admin or creator)
@bot.command(name="winner")
async def declare_result(ctx, bet_id: int, winning_option: int):
    if bet_id not in active_bets:
        await ctx.send(
            embed=discord.Embed(
                description="Bet ID not found!", color=discord.Color.red()
            )
        )
        return

    bet = active_bets[bet_id]

    if "options" not in bet or winning_option not in bet["options"]:
        await ctx.send(
            embed=discord.Embed(
                description="Invalid options for this bet.", color=discord.Color.red()
            )
        )
        return

    # Declare the winning option (1 or 2)
    winning_option_str = str(winning_option)
    bet["winner"] = winning_option_str

    # List of winners
    winners = []

    # Update stats based on user choices for this bet
    if "user_choices" in bet:
        participants = bet["user_choices"]
        for user_name, choice in participants.items():
            if choice == winning_option_str:
                update_stats(user_name, "win")
                winners.append(user_name)  # Add user to the list of winners
            else:
                update_stats(user_name, "loss")

    # Save updated stats and remove bet from active bets
    save_stats(user_stats)
    del active_bets[bet_id]
    save_bets(active_bets)

    # Inform the channel of the result
    winning_text = bet["options"][winning_option]
    if winners:
        winners_text = ", ".join(winners)
    else:
        winners_text = "No one"

    embed = discord.Embed(
        title=f"**Bet:** {bet['bet_name']}\nResults: {winning_text}",
        description=f"Winners: {winners_text}",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed)


# Command to view active bets
@bot.command(name="bets")
async def view_bets(ctx):
    if not active_bets:
        embed = discord.Embed(
            description="No active bets.", color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title="Active Bets", color=discord.Color.blue())
    for bet_id, bet in active_bets.items():
        if "options" in bet and 1 in bet["options"] and 2 in bet["options"]:
            options_text = f"{bet['options'][1]}, {bet['options'][2]}"
            embed.add_field(
                name=f"**Bet**: {bet['bet_name']}",
                value=f"**Creator**: {bet['creator']} | **Bet ID**: {bet_id}",
                inline=False,
            )
        else:
            embed.add_field(
                name=f"**Bet**: {bet['bet_name']}",
                value=f"**Creator**: {bet['creator']} | **Bet ID**: {bet_id}",
                inline=False,
            )

    await ctx.send(embed=embed)


# Command to view user stats
@bot.command(name="stats")
async def stats(ctx, member: discord.Member = None):
    member = member or ctx.author

    if member.name not in user_stats:
        embed = discord.Embed(
            description=f"{member.name} has no recorded stats yet.",
            color=discord.Color.orange(),
        )
        await ctx.send(embed=embed)
        return

    wins = user_stats[member.name]["wins"]
    losses = user_stats[member.name]["losses"]

    embed = discord.Embed(
        title=f"{member.name}'s Stats",
        description=f"Wins: {wins}\nLosses: {losses}",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed)


# Function to update stats
def update_stats(user_name: str, result: str):
    if user_name not in user_stats:
        user_stats[user_name] = {"wins": 0, "losses": 0}

    if result == "win":
        user_stats[user_name]["wins"] += 1
    elif result == "loss":
        user_stats[user_name]["losses"] += 1

    save_stats(user_stats)


# Command to delete a bet by its ID
@bot.command(name="dbet")
async def delete_bet(ctx, bet_id: int):
    if bet_id not in active_bets:
        embed = discord.Embed(
            description="Bet ID not found! Please provide a valid bet ID.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        return

    del active_bets[bet_id]
    save_bets(active_bets)

    embed = discord.Embed(
        description=f"Bet with ID {bet_id} has been successfully deleted.",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed)


# Global error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            description="Sorry, that command doesn't exist. Use `!help` to see the available commands.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            description="It seems like you're missing some arguments. Please check the command and try again.",
            color=discord.Color.orange(),
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            description="There seems to be a problem with the argument you've provided.",
            color=discord.Color.orange(),
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description="An unexpected error occurred. Please try again.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        print(f"Unhandled error: {error}")


# Start the bot with your token from .env file
bot.run(TOKEN)
