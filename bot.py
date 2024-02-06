# noinspection PyUnresolvedReferences
import discord
from discord import Message, TextChannel, Thread, Guild, Intents, Client, User, Member, Permissions, Role
from enum import Enum, auto
from typing import cast
from numpy.random import choice

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

	class ReplyCondition(Enum):
		IS_CONFIRMED = auto()
		IS_SEND_TO_ALL = auto()

	# region members
	SEND_DM_EXPECTED_ARGUMENTS: list  # type: ignore

	server: Server
	from_user: User | Member
	channel: ServerTextChannel

	command_error = Error.OK
	command_error_message: str

	# send_dm
	to_all = False
	to_user: User | Member
	# endregion

	def __init__(self, server: Server, user: User | Member, channel: ServerTextChannel) -> None:
		self.server = server
		self.from_user = user
		self.channel = channel


	async def send_dm(self, user_message: str) -> None:

		user_permission: Permissions = self.channel.permissions_for(cast(Member | Role, self.from_user))
		if not user_permission.mention_everyone:
			await self.channel.send("Dir fehlen die Berechtigungen für diesen Befehl.")
			return

		user_arguments: list[str] = user_message.split(" ")

		for user_argument in user_arguments:

			if user_argument == "":
				continue

			if self.get_user_id(user_argument) == Command.Error.OK:
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

		direct_message = await self.wait_for_reply(300, Command.ReplyCondition.IS_SEND_TO_ALL)
		if direct_message is None:
			return

		message = await self.wait_for_reply(15, Command.ReplyCondition.IS_CONFIRMED)
		if message is None:
			return

		if self.to_all:
			for member in self.server.members:
				if member.bot:
					continue
				await member.send(direct_message.content)
			await self.channel.send("Nachrichten wurden versendet :3")
		else:
			await self.to_user.send(direct_message.content)
			await self.channel.send("Nachricht wurde versendet :3")


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


	def assert_user_id_is_int(self, value: str) -> bool:
		try:
			int(value)
		except ValueError:
			self.command_error_message = value
			self.command_error = Command.Error.USER_ID_NOT_INT
			return False
		return True


	def is_reply_original_author(self, reply: Message) -> bool:
		return reply.author == self.from_user


	async def wait_for_reply(self, timeout: int, condition: ReplyCondition) -> Message | None:
		try:
			message = await client.wait_for("message", check=self.is_reply_original_author, timeout=timeout)
		except TimeoutError:
			await self.channel.send(
				self.from_user.mention + " Timeout: Befehl abgebrochen. Es wurde keine DM versendet."
			)
			return None

		# TODO wat is dis
		else:
			if Command.check_condition(self, message.content, condition):
				match condition:
					case Command.ReplyCondition.IS_CONFIRMED:
						pass
					case Command.ReplyCondition.IS_SEND_TO_ALL:
						await self.channel.send("""
Sicher, dass du folgende Nachricht an **ALLE User in diesem Server** per DM senden willst?
### Nachricht:
{message}
""".format(message=message.content)
						)
			else:
				match condition:
					case Command.ReplyCondition.IS_CONFIRMED:
						await self.channel.send("Nicht bestätigt: Befehl abgebrochen. Es wurde keine DM versendet.")
						return None
					case Command.ReplyCondition.IS_SEND_TO_ALL:
						await self.channel.send("""
Sicher, dass du folgende Nachricht an **{user}** per DM senden willst?
### Nachricht:
{message}
""".format(user=self.to_user, message=message.content)
						)
		return message


	def check_condition(self, message: str, condition: ReplyCondition) -> bool:
		match condition:
			case Command.ReplyCondition.IS_CONFIRMED:
				return message == "Ja"
			case Command.ReplyCondition.IS_SEND_TO_ALL:
				return self.to_all


@client.event
async def on_ready() -> None:
	print("NikkiBot is up and running :3")


@client.event
async def on_message(message: Message) -> None:
	if message.guild is None:
		return

	server_text_channel: ServerTextChannel
	server_text_channel = cast(ServerTextChannel, message.channel)

	server: Server = message.guild

	if message.author == client.user:
		return

	command = Command(server, message.author, server_text_channel)
	is_valid_message = False

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
		if not user_message == "":
			await command.send_dm(user_message)
			is_valid_message = True

	if message.content.startswith(PREFIX) and not is_valid_message:
		a: list[str] = []
		for unvalid_response in unvalid_responses:
			a.append(unvalid_response)
		p: list[float] = get_normalized_probability_weights()
		random_unvalid_response: str = choice(a=a, p=p)
		if not random_unvalid_response.find("{user}") == -1:
			random_unvalid_response = random_unvalid_response.format(user=message.author.name)
		await message.channel.send(random_unvalid_response)


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
