import socket
from time import sleep


def main():
    HOST = "127.0.0.1"
    PORT = 1234

    MAX_SIZE_MESSAGE_B = 1024

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        too_long_message = bytes("".join(
            ["X" for i in range(MAX_SIZE_MESSAGE_B * 2)]
        ), "utf-8")

        s.sendall(too_long_message)
        sleep(1)


if __name__ == "__main__":
    main()
