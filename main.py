import asyncio
import sys
import threading
import py.bot as bot
# noinspection PyUnresolvedReferences
from py.sftp import SFTPClient


async def wait() -> None:
	await asyncio.sleep(10)


async def main() -> None:
	t1 = threading.Thread(target=bot.run, daemon=True)
	t1.start()
	while True:
		await wait()
		print("10 seconds over")


if __name__ == "__main__":
	# logging.basicConfig(level=logging.DEBUG)
	# SFTPClient(SFTPClient.Actions.SEND_TO_FILE)
	# py.bot.dm_logs
	sys.exit(asyncio.run(main()))
