import logging
import discord
from discord.ext import commands

TOKEN = "MTIwMjE2NzAyOTY2NzIwNTE0MQ.GcDc5x.6Eb7cZ7Xln8Qg7P74-twUev7SFm2jxFr6aoljE"

intents = discord.Intents.default()
intents.message_content = True
# intents.presences = True
# intents.members = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

@client.event
async def on_ready():
    print(f"NikkiBot is up and running :3")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

@bot.command
async def test(ctx, arg):
    await ctx.send("hewwo :3")


client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)

bot.add_command(test)