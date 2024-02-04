import discord

msg = discord.Message
ch = discord.abc.Messageable

PREFIX = "!Nikki, "
TOKEN: str
with open("token", encoding="utf-8") as f:
    TOKEN = f.read()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

class CMD:

    @staticmethod
    async def say_neko_smile(channel: ch) -> None:
        await channel.send(":3")


    @staticmethod
    async def send_dm_all(argument: msg, channel: ch) -> None:
        await channel.send(argument)


@client.event
async def on_ready() -> None:
    print("NikkiBot is up and running :3")


@client.event
async def on_message(message: msg) -> None:

    if message.author == client.user:
        return

    await in_any_guild(message)

    if message.guild.name == "Doomertreffpunkt":
        await in_doomertreffpunkt(message)

    if message.guild.name == "Geheimlabor":
        await in_geheimlabor(message)


async def in_any_guild(message: msg) -> None:

    if message.content.casefold().startswith("good girl"):
        await CMD.say_neko_smile(message.channel)

    if message.content.find(":3") != -1:
        await CMD.say_neko_smile(message.channel)


async def in_doomertreffpunkt(message: msg) -> None:
    if not (message.channel.id == 1115389541696667879 and message.channel.category.id == 1113691175803695124):
        return


async def in_geheimlabor(message: msg) -> None:
    if message.content.startswith(PREFIX + "sende DM an"):
        argument = message.content.removeprefix(PREFIX + "sende DM an")
        await CMD.send_dm_all(argument, message.channel)


client.run(TOKEN)
