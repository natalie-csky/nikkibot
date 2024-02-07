import asyncio
from multiprocessing import Process, Pipe
import sys
import py.bot as bot
# noinspection PyUnresolvedReferences
from py.sftp import SFTPClient


async def wait_time() -> None:
	await asyncio.sleep(10)


async def main() -> int:
	parent_conn, child_conn = Pipe()
	p = Process(target=bot.run, name="nikki_bot", args=(child_conn,))
	p.start()
	await wait_time()
	print(parent_conn.recv())
	print("BEFORE CHILD TERMINATED")
	p.terminate()
	print("AFTER CHILD TERMINATED")
	p.close()
	print("main.py ended gracefully")
	return 0


if __name__ == "__main__":
	# SFTPClient(SFTPClient.Actions.SEND_TO_FILE)
	# py.bot.dm_logs
	sys.exit(asyncio.run(main()))
