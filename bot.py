import discord
import random
from numpy.random import choice

#region members

Msg = discord.Message
Ch = discord.abc.Messageable
Server = discord.Guild

PREFIX = "!Nikki, "
BOT_NAME = "NikkiBot"

TOKEN_FILE = "token"
TOKEN: str

with open(TOKEN_FILE, encoding="utf-8") as f:
    TOKEN = f.read()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

is_valid_message: bool

unvalid_responses: dict[str, int] = {
    "Hm?": 20,
    "Wat?": 20,
    "Was laberst du?": 15,
    "Hascht du überhaupt gelernt, Alter, was labersch du?": 7,
    "Was du am Labern bist hab ich gefragt.": 7,
    "Excusez-moi?": 15,
    "Bitte gehen Sie Ihre Anfrage nochmal Wort für Wort durch. Danke.": 3,
    "Leute wie dich sind der Grund warum es Anleitungen auf Shampooflaschen gibt.": 2,
    "Red Deutsch.": 12,
    "Sprich Deutsch.": 12,
    "Sprich Klartext.": 12,
    "Red mal Klartext.": 12,
    "?": 15,
    "???": 15,
    "!?": 15,
    "Entschuldigung?": 17,
    "Bitte was?": 17,
    "Mein IQ ist ja garnicht mal sooo weit von deinem entfernt.": 1,
    "Nah dran, glaub ich. Versuch nochmal.": 15,
    "Wie war das? Ich versteh dich nicht so gut.": 7,
    "error (value < 0): user iq too low": 2,
    "{user} befehligt " + BOT_NAME + "! Es ist nicht sehr effektiv...": 2,
    "Frag doch einfach nochmal.": 4,
    "Du schreibst nämlich mit h, oder?": 2
}

#endregion

class CMD:

    @staticmethod
    async def say_neko_smile(channel: Ch) -> None:
        await channel.send(":3")


    @staticmethod
    async def send_dm(user_msg: str, channel: Ch) -> None:

        server: Server = channel.guild

        arguments: list[str] = user_msg.split(" ")
        argument_count: int = 0

        to_all = False
        user_id: int

        for argument in arguments:

            if argument == "":
                continue

            match argument_count:

                case 0:
                    if argument.casefold() == "alle":
                        to_all = True
                        argument_count += 1
                        continue


@client.event
async def on_ready() -> None:
    print("NikkiBot is up and running :3")


@client.event
async def on_message(message: Msg) -> None:

    is_valid_message = False

    if message.author == client.user:
        return

    is_valid_message = await in_any_guild(message)

    if message.guild.name == "Doomertreffpunkt":
        is_valid_message = await in_doomertreffpunkt(message)

    if message.guild.name == "Geheimlabor":
        is_valid_message = await in_geheimlabor(message)

    if message.content.startswith(PREFIX) and not is_valid_message:
        a: list[str] = []
        for unvalid_response in unvalid_responses:
            a.append(unvalid_response)
        p: list[float] = get_normalized_probability_weights()
        unvalid_response: str = choice(a=a, p=p)
        if not unvalid_response.find("{user}") == -1:
            unvalid_response = unvalid_response.format(user = message.author.name)
        await message.channel.send(unvalid_response)


def get_normalized_probability_weights() -> list[float]:
    weight_total: float = 0.0
    for unvalid_response in unvalid_responses:
        weight_total += unvalid_responses[unvalid_response]

    weight_modifier: float = 1 / weight_total
    normalized_weights: list[float] = []

    for unvalid_response in unvalid_responses:
        normalized_weight: float = weight_modifier * unvalid_responses[unvalid_response]
        normalized_weights.append(normalized_weight)

    return normalized_weights


async def in_any_guild(message: Msg) -> bool:

    if message.content.casefold().startswith("good girl"):
        await CMD.say_neko_smile(message.channel)
        return True

    if message.content.find(":3") != -1:
        await CMD.say_neko_smile(message.channel)
        return True

    return False


async def in_doomertreffpunkt(message: Msg) -> bool:
    if not (message.channel.id == 1115389541696667879 and message.channel.category.id == 1113691175803695124):
        return

    return False


async def in_geheimlabor(message: Msg) -> bool:
    if message.content.startswith(PREFIX + "sende DM an"):
        user_msg = message.content.removeprefix(PREFIX + "sende DM an")
        await CMD.send_dm(user_msg, message.channel)
        return True

    return False


client.run(TOKEN)
