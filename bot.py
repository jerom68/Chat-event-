import discord
from discord.ext import commands, tasks
import json
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents)

# Load settings from the settings.json file
def load_settings():
    with open('settings.json', 'r') as file:
        return json.load(file)

settings = load_settings()

# Define global variables
message_count = {}

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Track messages in the specified channel
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if message is in the right channel
    if message.channel.id == int(os.environ['MESSAGE_CHANNEL_ID']):
        if message.author.id not in message_count:
            message_count[message.author.id] = 0

        message_count[message.author.id] += 1

        # If user reaches 100 messages, give them a box
        if message_count[message.author.id] == 100:
            user = message.author
            await send_box_embed(user)
            message_count[message.author.id] = 0  # Reset count after reward

    await bot.process_commands(message)

# Send the box embed when user reaches 100 messages
async def send_box_embed(user):
    embed = discord.Embed(
        title=f"Congrats, {user.name}!",
        description=f"Hey <@{user.id}>, you've sent 100 messages in the chat and earned a mysterious box!\n\n"
                    f"Use `+openbox` to reveal your reward.\n**Tip:** Take a screenshot when you open your box!",
        color=discord.Color.green()
    )
    embed.set_footer(text="Keep chatting to earn more boxes!")

    await user.send(embed=embed)

# Command: +help - Shows the help message
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help - Chat Event Bot",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(name="+messages", value="Check your progress towards the next box.", inline=False)
    embed.add_field(name="+myboxes", value="See how many boxes you have.", inline=False)
    embed.add_field(name="+openbox", value="Open one box to reveal your reward.", inline=False)
    embed.add_field(name="+help", value="Shows this help message.", inline=False)

    await ctx.send(embed=embed)

# Command: +myboxes - Check how many boxes the user has
@bot.command()
async def myboxes(ctx):
    user = ctx.author
    # You can later implement tracking for how many boxes the user has earned
    embed = discord.Embed(
        title=f"{user.name}'s Boxes",
        description=f"You currently have X boxes ready to open!",
        color=discord.Color.yellow()
    )
    await ctx.send(embed=embed)

# Command: +openbox - Open a box and get a random reward
@bot.command()
async def openbox(ctx):
    user = ctx.author
    reward = random.choice(settings["rewards"])

    embed = discord.Embed(
        title="You Opened a Box!",
        description=f"Congratulations, <@{user.id}>! You've earned: **{reward}**.",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

# Command to reload settings
@bot.command()
async def reload_settings(ctx):
    global settings
    settings = load_settings()
    await ctx.send("Settings reloaded successfully.")

# Start the bot with your token from environment variables
bot.run(os.environ['TOKEN'])
