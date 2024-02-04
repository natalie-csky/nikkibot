import discord

TOKEN = "MTIwMjE2NzAyOTY2NzIwNTE0MQ.GcDc5x.6Eb7cZ7Xln8Qg7P74-twUev7SFm2jxFr6aoljE"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

PREFIX = "!Nikki, "

@client.event
async def on_ready() -> None:
    print("NikkiBot is up and running :3")


@client.event
async def on_message(message: discord.Message) -> None:

    if message.author == client.user:
        return

    if message.guild.name == "Doomertreffpunkt":
        await in_doomertreffpunkt(message)
    
    if message.guild.name == "Geheimlabor":
        await in_geheimlabor(message)
    
    
async def in_doomertreffpunkt(message: discord.Message) -> None:
    if not (message.channel.name == "botausbeutung" and message.channel.category.name == "chefetage"):
            return

    if message.content.startswith("Good girl") or message.content.startswith("good girl"):
        await message.channel.send(":3")
    
    if message.content.find(":3") != -1:
        await message.channel.send(":3")


async def in_geheimlabor(message: discord.Message) -> None:
    if message.content.startswith(PREFIX + "sende DM an"):
        arguments = message.content.removeprefix(PREFIX + "sende DM an")
        await message.channel.send(arguments)


client.run(TOKEN)
