import asyncio
from bleach.sanitizer import Cleaner
import sys
import threading

import py.bot as bot
from py.sftp import SFTPClient

ALLOWED_TAGS = frozenset({'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul'})

async def wait() -> None:
	await asyncio.sleep(10)


async def main() -> None:
	bot_thread = threading.Thread(target=bot.run, daemon=True)
	bot_thread.start()
	while True:
		await wait()
		f = open("logs/logs.txt", "a")
		for log in bot.dm_logs:
			f.write(log)
			f.write("\n")
		f.close()

		if len(bot.dm_logs) > 0:
			sanitized_logs: list[str] = []

			cleaner = Cleaner(tags=ALLOWED_TAGS, strip=True)
			for log in bot.dm_logs:
				sanitized_logs.append(cleaner.clean(log))
			print("sending logs to webpage")
			SFTPClient(SFTPClient.Actions.SEND_TO_FILE, "doom_de/user_logs/logs.html", sanitized_logs)
			bot.dm_logs.clear()


if __name__ == "__main__":
	sys.exit(asyncio.run(main()))
