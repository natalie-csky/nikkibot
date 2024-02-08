import asyncio
import sys
import threading

import py.bot as bot
from py.sftp import SFTPClient


async def wait() -> None:
	await asyncio.sleep(10)


async def main() -> None:
	bot_thread = threading.Thread(target=bot.run, daemon=True)
	bot_thread.start()
	while True:
		await wait()
		if len(bot.dm_logs) > 0:
			SFTPClient(SFTPClient.Actions.SEND_TO_FILE, "doom_de/user_logs/logs.html", bot.dm_logs)
			bot.dm_logs.clear()


if __name__ == "__main__":
	sys.exit(asyncio.run(main()))
