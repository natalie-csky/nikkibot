# noinspection PyUnresolvedReferences
import discord
from discord import Message, TextChannel, Thread, Guild, Intents, Client, User, Member
from enum import Enum
from typing import cast
# from numpy.random import choice

# region members

# region type aliases
ServerTextChannel = TextChannel | Thread
Server = Guild
# endregion

PREFIX = "!Nikki, "
BOT_NAME = "NikkiBot"

CONTINUE = object()

# region token setup
TOKEN_FILE = "token"
TOKEN: str
with open(TOKEN_FILE, encoding="utf-8") as f:
	TOKEN = f.read()
# endregion

# region client setup
intents = Intents.default()
intents.message_content = True
intents.members = True
client = Client(intents=intents)
# endregion

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
		"Wie war das? Ich versteh dich nicht so gut.": 6,
		"error (value < 0): user iq too low": 2,
		"{user} befehligt " + BOT_NAME + "! Es ist nicht sehr effektiv...": 2,
		"Frag doch einfach nochmal.": 6,
		"Du schreibst nämlich mit h, oder?": 2
}

# endregion

class CMD:
	class CommandError(Enum):
		OK = 0,
		USER_ID_NOT_INT = 1,
		USER_ID_NOT_FOUND = 2

	server: Server
	user: User | Member
	channel: ServerTextChannel

	to_all = False
	command_error = CommandError.OK
	command_error_message: str

	# @staticmethod
	# async def say_neko_smile(channel: ServerTextChannel) -> None:
	# 	await channel.send(":3")

	def __init__(self, server: Server, user: User | Member, channel: ServerTextChannel) -> None:
		self.server = server
		self.user = user
		self.channel = channel


	async def send_dm(self, user_message: str) -> None:

		valid_arguments: list = [  # type: ignore
			self.get_user_id
		]

		arguments: list[str] = user_message.split(" ")
		user_id: int

		argument_count: int = 0
		for argument in arguments:

			if argument == "":
				continue

			if valid_arguments[argument_count](argument) == CONTINUE:
				argument_count += 1
				continue

			match self.command_error:
				case CMD.CommandError.USER_ID_NOT_INT:
					await self.channel.send("user_id ist keine Nummer oder \'alle\'")
				case CMD.CommandError.USER_ID_NOT_FOUND:
					await self.channel.send("user_id " + self.command_error_message + " nicht gefunden")


	def get_user_id(self, argument: str) -> object:

		if argument.casefold() == "alle":
			self.to_all = True
			return CONTINUE

		for member in self.server.members:

			if member.bot:
				continue

			user_id: int = member.id

			try:
				int(argument)
			except ValueError:
				self.command_error = CMD.CommandError.USER_ID_NOT_INT
				return None

			if not user_id == int(argument):
				continue

			maybe_user: User | None = client.get_user(user_id)
			if maybe_user is None:
				self.command_error_message = str(user_id)
				self.command_error = CMD.CommandError.USER_ID_NOT_FOUND
				return None

			self.user = maybe_user
			return CONTINUE

		return None


@client.event
async def on_ready() -> None:
	print("NikkiBot is up and running :3")


@client.event
async def on_message(message: Message) -> None:
	assert(message.guild is not None), "Message has no server associated with it"

	server_text_channel: ServerTextChannel
	# print(message.channel is not ServerTextChannel)
	# if message.channel is not ServerTextChannel:
	# 	return
	server_text_channel = cast(ServerTextChannel, message.channel)

	server: Server = message.guild

	if message.author == client.user:
		return

	cmd = CMD(server, message.author, server_text_channel)
	# is_valid_message = False

	# is_valid_message = await in_any_guild(message)

	server_text_channel = cast(ServerTextChannel, message.channel)
	assert(server_text_channel.category is not None)

	# only doomertreffpunkt and only chefetage botausbeutung channel
	# any other server, any channel
	if server.id == 1011019396577243307 \
		and not (server_text_channel.id == 1115389541696667879 and server_text_channel.category.id == 1113691175803695124):
		return

	if message.content.startswith(PREFIX + "sende DM an"):
		user_message = message.content.removeprefix(PREFIX + "sende DM an")
		await cmd.send_dm(user_message)

	# if message.content.startswith(PREFIX) and not is_valid_message:
	# 	a: list[str] = []
	# 	for unvalid_response in unvalid_responses:
	# 		a.append(unvalid_response)
	# 	p: list[float] = get_normalized_probability_weights()
	# 	random_unvalid_response: str = choice(a=a, p=p)
	# 	if not random_unvalid_response.find("{user}") == -1:
	# 		random_unvalid_response = random_unvalid_response.format(user=message.author.name)
	# 	await message.channel.send(random_unvalid_response)


# async def in_any_guild(message: Message) -> bool:
#
# 	if message.content.casefold().startswith("good girl"):
# 		await CMD.say_neko_smile(cast(ServerTextChannel, message.channel))
# 		return True
#
# 	if message.content.find(":3") != -1:
# 		await CMD.say_neko_smile(cast(ServerTextChannel, message.channel))
# 		return True
#
# 	return False
#


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


client.run(TOKEN)
