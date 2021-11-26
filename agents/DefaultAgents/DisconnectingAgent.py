import socket
from time import sleep


def main():
    HOST = "127.0.0.1"
    PORT = 1234

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        sleep(0.5)


if __name__ == "__main__":
    main()
