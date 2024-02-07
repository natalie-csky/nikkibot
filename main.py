import asyncio
import sys

# noinspection PyUnresolvedReferences
import py.bot
# noinspection PyUnresolvedReferences
from py.sftp import SFTPClient


async def wait_for_time() -> None:
	await asyncio.sleep(10)


def main() -> int:
	print("hi :3")
	asyncio.run(wait_for_time())
	print("time's up")
	return 0


if __name__ == "__main__":
	# SFTPClient(SFTPClient.Actions.SEND_TO_FILE)
	# py.bot.dm_logs
	sys.exit(main())
