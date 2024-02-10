# import pytz
from datetime import datetime
from enum import Enum, auto
from numpy.random import choice
from typing import cast, TypeAlias, Union

# noinspection PyUnresolvedReferences
import discord
from discord import Message, TextChannel, DMChannel, Thread, Guild, VoiceChannel, StageChannel, Intents, Client, \
					User, Member, Permissions, Role

# region members

# region type aliases
ServerTextChannel: TypeAlias = TextChannel | Thread
TextableChannel: TypeAlias = Union[VoiceChannel, StageChannel, TextChannel, Thread]  # why
Server: TypeAlias = Guild
Author: TypeAlias = Member | User
# endregion

PREFIX = "!n "
BOT_NAME = "NikkiBot"

NIKKI_DM_ID = 1204362891289960468
DOOMERTREFFPUNKT_ID = 1011019396577243307
BOTAUSBEUTUNG_ID = 1115389541696667879
CHEFETAGE_ID = 1113691175803695124

DOG_MIDDLE_FINGER = "https://cdn.discordapp.com/stickers/898626750253269094.png"

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
	"Hascht du überhaupt gelernt, Alter, was labersch du?": 6,
	"Was du am Labern bist hab ich gefragt.": 6,
	"Excusez-moi?": 15,
	"Bitte gehen Sie Ihre Anfrage nochmal Wort für Wort durch. Danke.": 3,
	"Leute wie dich sind der Grund warum es Anleitungen auf Shampooflaschen gibt.": 4,
	"Red Deutsch.": 9,
	"Sprich Deutsch.": 9,
	"Sprich Klartext.": 9,
	"Red mal Klartext.": 9,
	"?": 15,
	"???": 15,
	"!?": 15,
	"Entschuldigung?": 17,
	"Bitte was?": 17,
	"Mein IQ ist ja garnicht mal sooo weit von deinem entfernt.": 3,
	"Nah dran, glaub ich. Versuch nochmal.": 15,
	"Wie war das? Ich versteh dich nicht so gut.": 7,
	"error (value < 0): user iq too low": 4,
	"{user} befehligt " + BOT_NAME + "! Es ist nicht sehr effektiv...": 4,
	"Frag doch einfach nochmal.": 7,
	"Du schreibst nämlich mit h, oder?": 4,
	DOG_MIDDLE_FINGER: 6
}

# # TODO DELETE
# MAX_TIME = datetime(2024, 2, 3, tzinfo=pytz.utc)
# MAX_TIME = MAX_TIME.replace(tzinfo=timezone.utc)

message_logs: list[str] = []
dm_logs: list[str] = []

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
	joined_at: datetime

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
				# if cast(datetime, member.joined_at) > MAX_TIME:
				# 	continue
				# await self.channel.send("theoretisch wäre eine nachricht an: " + member.name + " gesendet worden.")
				try:
					await member.send(direct_message.content)
				except Exception as e:
					await self.channel.send("User " + member.name + ": " + str(e))
			await self.channel.send("Nachrichten wurden versendet :3")
		else:
			try:
				await self.to_user.send(direct_message.content)
			except Exception as e:
				await self.channel.send("User: " + self.to_user.name + ": " + str(e))
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
				self.joined_at = cast(datetime, member.joined_at)
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
	if message.author == client.user:
		return

	await relay_bot_dm(message)

	if message.guild is None:
		return

	server_text_channel: ServerTextChannel
	server_text_channel = cast(ServerTextChannel, message.channel)

	server: Server = message.guild

	command = Command(server, message.author, server_text_channel)
	is_valid_message = False

	server_text_channel = cast(ServerTextChannel, message.channel)
	assert (server_text_channel.category is not None)

	if server.id == DOOMERTREFFPUNKT_ID \
		and not \
		(server_text_channel.id == BOTAUSBEUTUNG_ID and server_text_channel.category.id == CHEFETAGE_ID):
		return

	if message.content.casefold().startswith(PREFIX + "sende dm an"):
		user_message = message.content.casefold().removeprefix(PREFIX + "sende dm an")
		if not user_message == "":
			await command.send_dm(user_message)
			is_valid_message = True

	if message.content.startswith(PREFIX) and not is_valid_message:
		await send_wat(message)

async def relay_bot_dm(message: Message) -> None:
	if isinstance(message.channel, discord.DMChannel):
		nikki_channel = cast(DMChannel, await client.fetch_channel(NIKKI_DM_ID))

		now = datetime.now()
		ts = datetime.timestamp(now)
		time = datetime.fromtimestamp(ts)

		await nikki_channel.send(time.strftime("%d-%m-%Y, %H:%M:%S - ") + "DM by: " + message.author.name)
		dm_logs.append(time.strftime("%d-%m-%Y, %H:%M:%S - ") + "DM by: " + message.author.name)

		if not message.content == "":
			await nikki_channel.send(message.content)
			dm_logs.append(message.content)
		for sticker in message.stickers:
			await nikki_channel.send(sticker.url)
			dm_logs.append(sticker.url)

async def send_wat(message: Message) -> None:
	a: list[str] = []
	for unvalid_response in unvalid_responses:
		a.append(unvalid_response)
	p: list[float] = get_normalized_probability_weights()
	random_unvalid_response: str = choice(a=a, p=p)
	if not random_unvalid_response.find("{user}") == -1:
		random_unvalid_response = random_unvalid_response.format(user=message.author.name)
	await message.channel.send(random_unvalid_response)

async def query_messages(server_id: int, channel_id: int, limit: int) -> list[Message]:
	server = await client.fetch_guild(server_id)
	if server is None:
		print("no server found")
		return list()
	channel = cast(ServerTextChannel, server.get_channel(channel_id))
	print(channel.name)
	return [message async for message in channel.history(limit=limit)]

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
