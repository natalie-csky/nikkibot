import configparser
import paramiko

from enum import Enum, auto
from typing import cast, Tuple, Union, Optional

SFTP_HOST_FILE = "sftp_host"
KNOWN_HOSTS = "/home/nikki_sky/.ssh/known_hosts"
ALGORITHM = "ssh-ed25519"

class SFTPNoSuppliedArgumentsError(Exception):
	"""Raised when the action of an SFTPClient was supplied no or false arguments."""

class SFTPClient:
	"""
	Args:
		action: an action the client should execute
			{Actions.SEND_TO_FILE}: append text to file
			{Actions.CLEAR_FILE}: clear file
		file: a file on the server
		text: an array of strings to append to a file

	Raises:
		SFTPNoSuppliedArgumentsError: An error occurred when the action of an SFTPClient was supplied no or false arguments.
	"""
	# TODO rework Actions as methods, duh
	class Actions(Enum):
		SEND_TO_FILE = auto()
		CLEAR_FILE = auto()

	sftp_client: paramiko.SFTPClient


	def __init__(self, action: Actions, file: Union[str, None] = None, text: Optional[list[str]] = None) -> None:
		# Paramiko documentation: https://docs.paramiko.org/en/latest/

		sftp_host, username, password = SFTPClient.setup_config()

		# loads all keys from known_hosts file
		hostkeys = paramiko.hostkeys.HostKeys(KNOWN_HOSTS)

		# from previous keys, gets keys associated with sftp_host
		host_fingerprint = cast(dict[str, paramiko.PKey], hostkeys.lookup(sftp_host))[ALGORITHM]

		try:
			# An SSH Transport attches to a stream (usually a socket), negotiates an encrypted session,
			# authenticates, and then creates stream tunnels, called channels, across the session.
			# Instances of this class may be used as context managers.

			# Note: In this case, an address (as a tuple) is being passed here, which connects a socket to that address
			# that will be used for communication.

			# noinspection PyTypeChecker
			transport = paramiko.Transport((sftp_host, 22))

			# This is a shortcut for start_client(), get_remote_server_key()
			# and Twransport.auth_passord() OR Transport.auto_publickey().
			# Use the above methods if you want more control.
			# Using this method negotiates encryption with the host server. On success, an encrypted session exists.
			transport.connect(username=username, password=password, hostkey=host_fingerprint)

			try:
				# from_transport() creates an SFTP client channel from an open Transport,
				# referring to a sftp session (channel) across the transport.
				# The SFTP conctructor then creates an SFTP client from a Channel
				# that already requested the "sftp" subsystem. (calling free_transport() does just that)
				self.sftp_client = cast(paramiko.SFTPClient, paramiko.SFTPClient.from_transport(transport))
				assert (self.sftp_client is not None), "could not connect to sftp server"

				if file is None:
					raise FileNotFoundError("no file specified")

				if action == SFTPClient.Actions.SEND_TO_FILE:
					if text is None:
						raise SFTPNoSuppliedArgumentsError("no text supplied")
					self.send_to_file(text=text, to_file=file)

				elif action == SFTPClient.Actions.CLEAR_FILE:
					self.clear_file(file=file)

				self.sftp_client.close()

			except Exception as e:
				print("SFTP failed due to error: " + str(e))

			# Close the SFTP session and its underlying channel.
			transport.close()

		except paramiko.ssh_exception.AuthenticationException as e:
			print("Can't connect to server: " + str(e))
		except Exception as e:
			print("Can't connect to server: " + str(e))


	def send_to_file(self, text: list[str], to_file: str) -> None:
		with self.sftp_client.open(to_file, "a") as file:
			file.write("<br />\n")
			for line in text:
				file.write("<br />\n" + line)


	def clear_file(self, file: str) -> None:
		self.sftp_client.open(file, "w").close()


	@staticmethod
	def setup_config() -> Tuple[str, str, str]:
		config = configparser.ConfigParser()
		config.read(SFTP_HOST_FILE)
		sftp_host = config.get("data", "sftp_host")
		username = config.get("data", "username")
		password = config.get("data", "password")
		return sftp_host, username, password
