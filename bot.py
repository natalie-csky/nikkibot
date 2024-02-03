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

    if message.author is discord.User:
        print("ello2")
        print(message.author)
        if message.author.channel == "botausbeutung" and message.author.channel.category == "chefetage":
            print("ello")

    if message.content.startswith("Good girl") or message.content.startswith("good girl"):
        await message.channel.send(":3")
    
    elif message.content.startswith(":3"):
        await message.channel.send(":3")
    
    elif message.content.startswith(PREFIX + "Nikki, create channel"):
        channel = await message.author.guild.create_text_channel("HajChannel")
    
    # elif message.content.startswith(PREFIX + "nikki, clone channel"):
    #     await clone(name="CoolName", )


client.run(TOKEN)
