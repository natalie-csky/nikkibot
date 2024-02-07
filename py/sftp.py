import configparser
import paramiko
from typing import cast, Tuple

SFTP_HOST_FILE = "sftp_host"
KNOWN_HOSTS = "/home/nikki_sky/.ssh/known_hosts"
ALGORITHM = "ssh-ed25519"

def setup_config() -> Tuple[str, str, str]:
	config = configparser.ConfigParser()
	config.read(SFTP_HOST_FILE)
	sftp_host = config.get("data", "sftp_host")
	username = config.get("data", "username")
	password = config.get("data", "password")
	return sftp_host, username, password


def not_main() -> None:
	sftp_host, username, password = setup_config()

	hostkeys = paramiko.hostkeys.HostKeys(KNOWN_HOSTS)
	host_fingerprint = cast(dict[str, paramiko.PKey], hostkeys.lookup(sftp_host))[ALGORITHM]

	try:
		tp = paramiko.Transport((sftp_host, 22))
		tp.connect(username=username, password=password, hostkey=host_fingerprint)

		try:
			sftp_client = paramiko.SFTPClient.from_transport(tp)
			assert(sftp_client is not None), "could not connect to sftp server"

			file_count = 0

			# Proof of concept - list first 10 files
			for file in sftp_client.listdir():
				print(str(file))
				file_count += 1

			sftp_client.close()
		except Exception as e:
			print("SFTP failed due to error: " + str(e))

		tp.close()
	except paramiko.ssh_exception.AuthenticationException as e:
		print("Can't connect to server: " + str(e))
	except Exception as e:
		print("Can't connect to server: " + str(e))


not_main()
