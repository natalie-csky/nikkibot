from discord import Message, TextChannel, Thread, Guild, Intents, Client, User
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
	server: Server
	user: User | None
	# channel: ServerTextChannel

	to_all = False
	user_id_not_int_error = False

	# @staticmethod
	# async def say_neko_smile(channel: ServerTextChannel) -> None:
	# 	await channel.send(":3")


	@staticmethod
	async def send_dm(user_msg: str, server: Server, channel: ServerTextChannel) -> None:

		valid_arguments: list = [  # type: ignore
			CMD.get_user_id
		]
		CMD.server = server

		arguments: list[str] = user_msg.split(" ")

		CMD.to_all = False
		user_id: int

		argument_count: int = 0
		for argument in arguments:

			if argument == "":
				continue

			if valid_arguments[argument_count](argument) == CONTINUE:
				argument_count += 1
				continue

			if CMD.user_id_not_int_error:
				await channel.send("user_id ist keine Nummer oder \'alle\'")


	@staticmethod
	def get_user_id(argument: str) -> object:

		if argument.casefold() == "alle":
			CMD.to_all = True
			return CONTINUE

		for member in CMD.server.members:

			if member.bot:
				continue

			user_id: int = member.id

			try:
				int(argument)
			except ValueError:
				CMD.user_id_not_int_error = True
				return None

			if not user_id == int(argument):
				continue

			CMD.user = client.get_user(user_id)
			return CONTINUE

		return None


@client.event
async def on_ready() -> None:
	print("NikkiBot is up and running :3")


@client.event
async def on_message(message: Message) -> None:
	assert(message.guild is not None), "Message has no server associated with it"
	server: Server = message.guild

	if message.author == client.user:
		return
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
		user_msg = message.content.removeprefix(PREFIX + "sende DM an")
		await CMD.send_dm(user_msg, server, cast(ServerTextChannel, message.channel))

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
