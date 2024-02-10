import asyncio
from bleach.sanitizer import Cleaner
from discord import Message
import sys
import threading
import py.bot as bot
from py.sftp import SFTPClient

ALLOWED_TAGS = frozenset({'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul'})

async def wait() -> None:
	await asyncio.sleep(10)


def log_to_file() -> None:
	f = open("logs/logs.txt", "a")
	for log in bot.dm_logs:
		f.write(log)
		f.write("\n")
	f.write("\n")
	f.close()


def log_to_webpage() -> None:
	sanitized_logs: list[str] = []
	cleaner = Cleaner(tags=ALLOWED_TAGS, strip=True)
	for log in bot.dm_logs:
		sanitized_logs.append(cleaner.clean(log))
	SFTPClient(SFTPClient.Actions.SEND_TO_FILE, "doom_de/user_logs/logs.html", sanitized_logs)


def query_messages(messages: list[Message]) -> None:
	payload: list[str] = []
	for message in messages:
		payload.append(message.content)
	SFTPClient(SFTPClient.Actions.SEND_TO_FILE, "doom_de/user_logs/logs.html", payload)


# noinspection PyUnreachableCode
async def main() -> None:
	bot_thread = threading.Thread(target=bot.run, daemon=True)
	bot_thread.start()
	await bot.on_ready()
	print("in main: bot is ready")
	# noinspection PyTypeChecker wtf
	messages: list[Message] = await bot.query_messages(880768960402948106, 880768960402948110, 10)
	query_messages(messages)
	return
	while True:
		await wait()

		if not len(bot.dm_logs):
			continue

		print("logging")
		log_to_file()
		log_to_webpage()

		bot.dm_logs.clear()


if __name__ == "__main__":
	sys.exit(asyncio.run(main()))
