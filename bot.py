import discord

TOKEN = "MTIwMjE2NzAyOTY2NzIwNTE0MQ.GcDc5x.6Eb7cZ7Xln8Qg7P74-twUev7SFm2jxFr6aoljE"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

PREFIX = "!"


@client.event
async def on_ready():
    print(f"NikkiBot is up and running :3")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("Good girl") or message.content.startswith("good girl"):
        await message.channel.send(":3")
    
    elif message.content.startswith(PREFIX + "create_channel"):
        await message.channel.send("will do :3")


client.run(TOKEN)
