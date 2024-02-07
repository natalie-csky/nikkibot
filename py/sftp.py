import paramiko
from typing import cast

KNOWN_HOSTS = "/home/nikki_sky/.ssh/known_hosts"
SFTP_HOST = "access995155803.webspace-data.io"
ALGORITHM = "ssh-ed25519"
USERNAME = "u115380384"
PASSWORD = "handgrip-freckles-proclaim"

def not_main() -> None:
	hostkeys = paramiko.hostkeys.HostKeys(KNOWN_HOSTS)
	host_fingerprint = cast(dict[str, paramiko.PKey], hostkeys.lookup(SFTP_HOST))[ALGORITHM]

	try:
		tp = paramiko.Transport((SFTP_HOST, 22))
		tp.connect(username=USERNAME, password=PASSWORD, hostkey=host_fingerprint)

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
