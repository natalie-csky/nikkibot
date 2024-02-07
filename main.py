import asyncio
import sys

# noinspection PyUnresolvedReferences
import py.bot
# noinspection PyUnresolvedReferences
from py.sftp import SFTPClient


async def wait_for_time() -> None:
	await asyncio.sleep(10)


async def a() -> None:
	await asyncio.sleep(5)
	print("a")


async def b() -> None:
	await asyncio.sleep(10)
	print("b")

async def main() -> int:
	with asyncio.Runner() as runner:
		runner.run(b())
		runner.run(a())
	return 0


if __name__ == "__main__":
	# SFTPClient(SFTPClient.Actions.SEND_TO_FILE)
	# py.bot.dm_logs
	sys.exit(asyncio.run(main()))
