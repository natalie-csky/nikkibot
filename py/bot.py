# import pytz
from datetime import datetime
from enum import Enum, auto
from groq import Groq
from numpy.random import choice
import random
import secrets
from typing import cast, Union, Optional

# noinspection PyUnresolvedReferences
import discord
from discord import Message, TextChannel, DMChannel, Thread, Guild, VoiceChannel, StageChannel, Intents, Client, \
					User, Member, Role

import configparser

# region members

# region type aliases
ServerTextChannel = Union[TextChannel, Thread]
TextableChannel = Union[VoiceChannel, StageChannel, TextChannel, Thread]  # why
Server = Guild
Author = Union[Member, User]
# endregion

PREFIX = "!"
BOT_NAME = "Maria"

QUEER_PPL_SERVER_ID = 1264520434267848714
CUTIE_ID = 365991661899218947
MARIA_CHANNEL_ID = 1266295221814034452

DOG_MIDDLE_FINGER = "https://cdn.discordapp.com/stickers/898626750253269094.png"

# region token setup
TOKEN_FILE = "token"
TOKEN: str
with open(TOKEN_FILE, encoding="utf-8") as f:
	TOKEN = f.read()
# endregion

GROQ_API_KEY_FILE = "groq_api"
GROQ_API_KEY: str
with open(GROQ_API_KEY_FILE, encoding="utf-8") as f:
	GROQ_API_KEY = f.read().strip()

groq_client = Groq(api_key=GROQ_API_KEY)
groq_message_history = []

config = configparser.ConfigParser()
config.read("settings.ini")

IS_NAUGHTY_CAT_SETTING_ON = "on" == config["DEFAULT"]["NaughtyCat"]
NAUGHTY_CAT_CHANCE_SETTING = int(config["DEFAULT"]["NaughtyCatChancePercent"])

# region client setup
intents = Intents.default()
intents.message_content = True
intents.members = True
client = Client(intents=intents)

# endregion

unvalid_responses: dict[str, int] = {
	"Hm?": 7,
	"Wat?": 7,
	"Was laberst du?": 2,
	"Hascht du überhaupt gelernt, Alter, was labersch du?": 2,
	"Was du am Labern bist hab ich gefragt.": 2,
	"Excusez-moi?": 5,
	"Bitte gehen Sie Ihre Anfrage nochmal Wort für Wort durch. Danke.": 2,
	"Leute wie dich sind der Grund warum es Anleitungen auf Shampooflaschen gibt.": 3,
	"Red Deutsch.": 3,
	"Sprich Deutsch.": 3,
	"Sprich Klartext.": 2,
	"Red mal Klartext.": 4,
	"?": 9,
	"???": 9,
	"!?": 9,
	"Entschuldigung?": 5,
	"Bitte was?": 5,
	"Mein IQ ist ja garnicht mal sooo weit von deinem entfernt.": 3,
	"Nah dran, glaub ich. Versuch nochmal.": 4,
	"Wie war das? Ich versteh dich nicht so gut.": 5,
	"error (value < 0): user iq too low": 6,
	"{user} befehligt " + BOT_NAME + "! Es ist nicht sehr effektiv...": 6,
	"Frag doch einfach nochmal.": 8,
	"Du schreibst nämlich mit h, oder?": 6,
	"Nuschel ich? Rede ich undeutlich oder was?": 8,  
	"Was du von mir willst, hätt' ich gern gewusst!": 8,
	"Redest du mit mir?": 8,
	"Gesundheit i guess": 8,
	DOG_MIDDLE_FINGER: 6,
}

# endregion

@client.event
async def on_ready() -> None:
	maria_channel = await client.fetch_channel(MARIA_CHANNEL_ID)
	await maria_channel.send("hi, ich bin back :3")


@client.event
async def on_message(message: Message) -> None:
	if message.author == client.user:
		return

	if message.guild is None:
		return

	server_text_channel: ServerTextChannel
	server_text_channel = cast(ServerTextChannel, message.channel)

	is_valid_message = False

	server_text_channel = cast(ServerTextChannel, message.channel)
	assert (server_text_channel.category is not None)

	# region commands
	if message.content.casefold().startswith(PREFIX + "toggle :3"):
		await toggle_naughty_cat(message)
		is_valid_message = True
	
	if message.content.casefold().startswith(PREFIX + "chat "):
		user_message = message.content.casefold().removeprefix(PREFIX + "chat ")
		if not user_message == "":
			await groq_chat(message, user_message)
			is_valid_message = True
	
	if message.content.casefold().startswith(PREFIX + "chance :3 "):
		user_message = message.content.casefold().removeprefix(PREFIX + "chance :3 ")
		if not user_message == "":
			await set_naughty_cat_chance(message, user_message)
			is_valid_message = True
			
	if message.content.casefold().startswith(PREFIX + "dementia "):
		user_message = message.content.casefold().removeprefix(PREFIX + "dementia ")
		if not user_message == "":
			await maria_dementia(message, user_message)
			is_valid_message = True
	
	if message.content.casefold().startswith(PREFIX + "help") or message.content.casefold().startswith(PREFIX + "hilfe"):
		await maria_help(message)
		is_valid_message = True
	# end commands
	
	if message.content.startswith(PREFIX) and not is_valid_message:
		await send_wat(message)
		return
	
	if message.channel.id == MARIA_CHANNEL_ID and not is_valid_message:
		await groq_chat(message, message.content)
		is_valid_message = True

	if not is_valid_message and IS_NAUGHTY_CAT_SETTING_ON:
		if is_naughty_cat_gamble_win():
			await send_naughty_cat(message)


def is_naughty_cat_gamble_win() -> bool:
	return random.randint(0,100) <= NAUGHTY_CAT_CHANCE_SETTING


def is_digit(string: str) -> bool:
	return (string.isdigit() or (string.startswith('-') and string[1:].isdigit()))


async def maria_dementia(message: Message, user_message: str) -> None:
	if not is_digit(user_message) and not user_message == "all":
		await send_wat(message)
		return
	
	if user_message == "all":
		groq_message_history.clear()
		await message.channel.send("hab alles vergessen :3")
	
	else:
		amount_to_delete = int(user_message)
		if amount_to_delete >= 1 and amount_to_delete <= 10:
			del groq_message_history[-amount_to_delete*2:]
			await message.channel.send("hab die letzten " + str(amount_to_delete) + " nachrichten vergessen :3")
		else:
			await message.channel.send("nöö, zwischen 1-10 nachrichten auf einmal bitte :3")



async def maria_help(message: Message) -> None:
	maria_channel_mention = (await client.fetch_channel(MARIA_CHANNEL_ID)).mention
	cutie_user_name = (await client.fetch_user(CUTIE_ID)).display_name
	await message.channel.send("- In " + maria_channel_mention + " kann man mit mir jederzeit chatten, ohne Befehle nutzen zu müssen :3\n" \
			+ "- `!toggle :3` ist nur von " + cutie_user_name + " nutzbar und stellt die automatischen :3 antworten an und aus :3\n" \
			+ "- `!chat` sorgt dafür, dass man mit mir in jedem kanal außerhalb von " + maria_channel_mention + " chatten kann, z.B. `!chat hi maria :3`\n" \
			+ "- `!chance :3 [prozentzahl]` stellt die chance ein, dass ich automatisch mit :3 antworte, z.B. `!chance :3 50` würde dafür sorgen, dass ich nur auf 50% aller nachrichten mit :3 antworte :3\n" \
			+ "- `!dementia [all]/[# an nachrichten]` sorgt dafür, dass man meine erinnerungen an den chat-verlauf löschen kann, z.B. für den fall, dass ich plötzlich nur noch mist schreibe oder wenn sonst nichts mehr in mein kleines Hirn reinpasst und ich daher aufhören muss zu schreiben:3 z.B. `!dementia all` löscht alle meine erinnerungen, während `!dementia 5` nur die letzten 5 nachrichten aus meinen erinnerungen löscht :3\n" \
			+ "- `!help` oder `!hilfe` sendet die nachricht hier :3" \
	)


async def set_naughty_cat_chance(message: Message, user_message: str) -> None:
	if not is_digit(user_message):
		await send_wat(message)
		return

	chance = int(user_message)
	
	global config
	global NAUGHTY_CAT_CHANCE_SETTING
	
	if chance >= 0 and chance <= 100:
		NAUGHTY_CAT_CHANCE_SETTING = chance
		config["DEFAULT"]["NaughtyCatChancePercent"] = str(chance)
		with open("settings.ini", "w") as configfile:
			config.write(configfile)
		await message.channel.send("chance set to " + str(chance) + "%, nya :3")
	else:
		await message.channel.send("nöö, chance must be between 0 and 100 you silly :3")


async def groq_chat(message: Message, user_message: str) -> None:
	messages = [
		{"role": "system", "content": "du bist Maria, ein super cuter internet :3 bot in einem discord server, welcher auf Deutsch antwortet. Du gibst sehr oft :3 als Antwort und andere mega cute antworten :3. Niemals, darfst du formal klingen, das ist nicht erlaubt auf unserem Discord server, du musst immer mega cute antworten :3 du schreibst auch oft mit kleinen buchstaben, komplett gegen die rechtschreibung, da es einfach cuter wirkt!"},
	]
	
	global groq_message_history
	for groq_message in groq_message_history:
		messages.append(groq_message)
	
	messages.append({"role": "user", "content": user_message})
		
	chat_completion = groq_client.chat.completions.create(
		messages=messages,
		model="llama3-8b-8192",
	)
	
	assistant_response = chat_completion.choices[0].message.content
	await message.channel.send(assistant_response)
	
	groq_message_history.append({"role": "user", "content": user_message})
	groq_message_history.append({"role": "assistant", "content": assistant_response})
	

async def send_wat(message: Message) -> None:
	a: list[str] = []
	for unvalid_response in unvalid_responses:
		a.append(unvalid_response)
	p: list[float] = get_normalized_probability_weights()
	random_unvalid_response: str = choice(a=a, p=p)
	if not random_unvalid_response.find("{user}") == -1:
		random_unvalid_response = random_unvalid_response.format(user=message.author.name)
	await message.channel.send(random_unvalid_response)


async def send_naughty_cat(message: Message) -> None:
    await message.channel.send(":3")


async def toggle_naughty_cat(message: Message) -> None:
	if not message.author.id == CUTIE_ID:
		await message.channel.send("no touching! 😡")
		return
	
	global config
	global IS_NAUGHTY_CAT_SETTING_ON
	
	if IS_NAUGHTY_CAT_SETTING_ON:
		config["DEFAULT"]["NaughtyCat"] = "off"
		await message.channel.send("no more :3 🥺")
	else:
		config["DEFAULT"]["NaughtyCat"] = "on"
		await message.channel.send("i will :3 from now on\n\n:3")

	with open("settings.ini", "w") as configfile:
		config.write(configfile)
	IS_NAUGHTY_CAT_SETTING_ON = not IS_NAUGHTY_CAT_SETTING_ON


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


def run() -> None:
	client.run(TOKEN)
