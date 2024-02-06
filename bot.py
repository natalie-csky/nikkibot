# noinspection PyUnresolvedReferences
import discord
from discord import Message, TextChannel, Thread, Guild, Intents, Client, User, Member
from enum import Enum, auto
from typing import cast
# from numpy.random import choice

# region members

# region type aliases
ServerTextChannel = TextChannel | Thread
Server = Guild
# endregion

PREFIX = "!n "
BOT_NAME = "NikkiBot"

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

class Command:
	class Error(Enum):
		OK = auto()
		FAILED = auto()
		USER_ID_NOT_INT = auto()
		USER_ID_NOT_FOUND = auto()

	SEND_DM_EXPECTED_ARGUMENTS: list  # type: ignore

	server: Server
	from_user: User | Member
	channel: ServerTextChannel

	command_error = Error.OK
	command_error_message: str

	# send_dm
	to_all = False
	to_user: User | Member


	def __init__(self, server: Server, user: User | Member, channel: ServerTextChannel) -> None:
		self.server = server
		self.from_user = user
		self.channel = channel


	async def send_dm(self, user_message: str) -> None:
		user_arguments: list[str] = user_message.split(" ")

		for expected_argument in Command.SEND_DM_EXPECTED_ARGUMENTS:
			argument_index: int = 0
			for user_argument in user_arguments:
				argument_index += 1

				if user_argument == "":
					continue

				if expected_argument(self, user_argument) == Command.Error.OK:
					break

				error_mesage: str = ""
				match self.command_error:
					case Command.Error.OK:
						continue
					case Command.Error.USER_ID_NOT_INT:
						error_mesage = "User ID \'" + self.command_error_message + "\' ist keine Nummer oder \'alle\'."
					case Command.Error.USER_ID_NOT_FOUND:
						error_mesage = "User ID \'" + self.command_error_message + "\' nicht gefunden."
				await self.channel.send(error_mesage)
				return

		await self.channel.send("Okay, bitte stelle deine Nachricht.")

		def check(reply: Message) -> bool:
			return reply.author == self.from_user

		try:
			message: Message = await client.wait_for("message", check=check, timeout=20)
		except TimeoutError:
			await self.channel.send(
				self.from_user.mention + " Timeout: Befehl abgebrochen. Es wurde keine DM versendet."
			)
		else:
			if self.to_all:
				await self.channel.send(
					"Sicher, dass du folgende Nachricht an ALLE User in diesem Server per DM senden willst? \n\n" +
					message.content
				)
			else:
				await self.channel.send(
					"Sicher, dass du folgende Nachricht an {user} per DM senden willst? \n\n".format(
						user=self.to_user
					) +
					message.content
				)
			await self.channel.send(
				"Sicher, dass du folgende Nachricht an {user} per DM senden willst?" +
				"Test"
			)


	def get_user_id(self, argument: str) -> object:

		if argument.casefold() == "alle":
			self.to_all = True
			return Command.Error.OK

		for member in self.server.members:

			if member.bot:
				continue

			if not self.assert_user_id_is_int(argument):
				return Command.Error.USER_ID_NOT_INT

			if member.id == int(argument):
				user_id = int(argument)
				maybe_user: User | None = client.get_user(user_id)
				self.to_user = cast(User | Member, maybe_user)
				return Command.Error.OK

		self.command_error_message = argument
		self.command_error = Command.Error.USER_ID_NOT_FOUND
		return Command.Error.USER_ID_NOT_FOUND


	def get_message(self, argument: str) -> object:
		pass

	def assert_user_id_is_int(self, value: str) -> bool:
		try:
			int(value)
		except ValueError:
			self.command_error_message = value
			self.command_error = Command.Error.USER_ID_NOT_INT
			return False
		return True


Command.SEND_DM_EXPECTED_ARGUMENTS = [
	Command.get_user_id
]


# async def timeout(time: int, channel: ServerTextChannel) -> None:
# 	await asyncio.sleep(time)
# 	await channel.send("Timeout: Befehl abgebrochen")


@client.event
async def on_ready() -> None:
	print("NikkiBot is up and running :3")


@client.event
async def on_message(message: Message) -> None:
	assert(message.guild is not None)

	server_text_channel: ServerTextChannel
	server_text_channel = cast(ServerTextChannel, message.channel)

	server: Server = message.guild

	if message.author == client.user:
		return

	command = Command(server, message.author, server_text_channel)
	# is_valid_message = False

	# is_valid_message = await in_any_guild(message)

	server_text_channel = cast(ServerTextChannel, message.channel)
	assert(server_text_channel.category is not None)

	# only doomertreffpunkt and only chefetage botausbeutung channel
	# any other server, any channel
	if server.id == 1011019396577243307 \
		and not \
		(server_text_channel.id == 1115389541696667879 and server_text_channel.category.id == 1113691175803695124):
		return

	if message.content.casefold().startswith(PREFIX + "sende dm an"):
		user_message = message.content.casefold().removeprefix(PREFIX + "sende dm an")
		await command.send_dm(user_message)

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
