# import logging
# import discord
# from discord.ext import commands

TOKEN = "MTIwMjE2NzAyOTY2NzIwNTE0MQ.GcDc5x.6Eb7cZ7Xln8Qg7P74-twUev7SFm2jxFr6aoljE"

# intents = discord.Intents.default()
# intents.message_content = True
# # intents.presences = True
# # intents.members = True

# # client = discord.Client(intents=intents)
# bot = commands.Bot(command_prefix="$", intents=intents)

# handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")


# @bot.event
# async def on_ready():
#     print(f"NikkiBot is up and running :3")


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if message.content.startswith("$hello"):
#         await message.channel.send("Hello!")


# @bot.command()
# async def test(ctx, arg):
#     await ctx.send(arg)


# bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)

import discord
from discord.ext import commands
import random


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)


@bot.event
async def on_ready():
    print(f"NikkiBot is up and running :3")


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


bot.run(TOKEN)