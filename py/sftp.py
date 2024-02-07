import configparser
import paramiko
from enum import Enum, auto
from typing import cast, Tuple

SFTP_HOST_FILE = "sftp_host"
KNOWN_HOSTS = "/home/nikki_sky/.ssh/known_hosts"
ALGORITHM = "ssh-ed25519"

class SFTPClient:
	class Actions(Enum):
		SEND_TO_FILE = auto()

	sftp_client: paramiko.SFTPClient


	def __init__(self, action: Actions, file: str, text: list[str]) -> None:
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

				match action:
					case SFTPClient.Actions.SEND_TO_FILE:
						self.send_to_file(text=text, to_file=file)

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
			for line in text:
				file.write("\n" + line)


	@staticmethod
	def setup_config() -> Tuple[str, str, str]:
		config = configparser.ConfigParser()
		config.read(SFTP_HOST_FILE)
		sftp_host = config.get("data", "sftp_host")
		username = config.get("data", "username")
		password = config.get("data", "password")
		return sftp_host, username, password


test = [
	"Hello World!",
	"Bye World!"
]

client = SFTPClient(SFTPClient.Actions.SEND_TO_FILE, text=test, file="doom_de/user_logs/logs.html")
