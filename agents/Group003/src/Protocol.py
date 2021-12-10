import socket
import subprocess
from sys import platform, stdout
from time import time_ns
from Colour import Colour
import shlex


class Protocol():
    """Static class that handles protocol communication between engine and
    agents. Uses a TCP socket.
    """

    HOST = "127.0.0.1"
    PORT = 1234
    s = None
    sockets = {Colour.RED: {}, Colour.BLUE: {}}

    @staticmethod
    def start():
        """Sets up a TCP server. The socket reuse address option is
        enabled because Linux does not close sockets immediately on
        application exit. This would cause issues with successive
        matches.
        """

        Protocol.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Protocol.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        Protocol.s.bind((Protocol.HOST, Protocol.PORT))
        Protocol.s.listen()

    @staticmethod
    def accept_connection(
        run_s,
        name,
        timeout_ns=30*10**9,
        silent=True,
        verbose=False
    ):
        """Starts a subprocess with the specified string then waits for the
        new process to connect to the socket. Returns True if the connection
        was made, False otherwise.
        """

        # separate run_s into a list of arguments to be used in a linux shell
        if (platform != "win32"):
            run_s = shlex.split(run_s)

        # determine the colour of the new agent
        if len(Protocol.sockets[Colour.RED].keys()) == 0:
            colour = Colour.RED
        elif len(Protocol.sockets[Colour.BLUE].keys()) == 0:
            colour = Colour.BLUE
        else:
            raise ValueError("Too many agents specified.")

        # whether to throw out all output of the agent
        # used to ease the screen clutter during the tournament
        output = stdout
        if (silent):
            output = subprocess.DEVNULL

        # start the agent
        t = subprocess.Popen(run_s, stdout=output, stderr=output, shell=False)

        # wait for a connection
        try:
            Protocol.s.settimeout(timeout_ns/10**9)
            conn, addr = Protocol.s.accept()
            Protocol.s.settimeout(socket.getdefaulttimeout())
            if verbose:
                print(f"Connected {name} at {addr}")
        except socket.timeout:
            conn, addr = None, None
            if (verbose):
                print(f"{name} never connected.")

        # set up associated arguments
        Protocol.sockets[colour]['name'] = name
        Protocol.sockets[colour]['thread'] = t
        Protocol.sockets[colour]['conn'] = conn
        Protocol.sockets[colour]['addr'] = addr

        return conn is not None

    @staticmethod
    def get_message(colour, timeout_ns=30*10**9, verbose=False):
        """Waits for a message from the given colour agent for the specified
        length of time. Returns the text and the associated wait time.
        """

        try:
            Protocol.sockets[colour]['conn'].settimeout(timeout_ns/10**9)
            move_time = time_ns()
            data = Protocol.sockets[colour]['conn'].recv(1024)
            move_time = time_ns() - move_time
            Protocol.sockets[colour]['conn'].settimeout(
                socket.getdefaulttimeout()
            )

        except socket.timeout:
            if verbose:
                print(
                    f"{Protocol.sockets[colour]['name']} timed out. " +
                    "Nothing received."
                )
            return ("NO MESSAGE", -1)
        except ConnectionResetError:
            if verbose:
                print(
                    f"{Protocol.sockets[colour]['name']} disconnected early.")
            return ("NO MESSAGE", -1)
        except Exception:
            if verbose:
                print(
                    f"{Protocol.sockets[colour]['name']} socket " +
                    "ended unexpectedly."
                )
            return ("NO MESSAGE", -1)

        if verbose:
            print(
                f"Received {data.decode('utf-8').strip()} from " +
                f"{Protocol.sockets[colour]['name']} in " +
                f"~{int(move_time/10**4)/10**5}s."
            )

        return (data.decode("utf-8"), move_time)

    @staticmethod
    def send_message(colour, message, verbose=False):
        """Sends the specified message to the specified colour agent."""

        try:
            Protocol.sockets[colour]['conn'].sendall(bytes(message, "utf-8"))
            if verbose:
                print("Sent", message, end="")

        except Exception:
            if verbose:
                print(
                    f"Failed to send {message.strip()} to " +
                    f"{Protocol.sockets[colour]['name']}."
                )

    @staticmethod
    def swap():
        """Switches the colours of the two agents."""

        Protocol.sockets[Colour.RED], Protocol.sockets[Colour.BLUE] = \
            Protocol.sockets[Colour.BLUE], Protocol.sockets[Colour.RED]

    @staticmethod
    def close(kill_children=True, verbose=False):
        """Closes the connection. If kill_children=True, it will also forcibly
        terminate the agents. Otherwise, it will block the thread until they
        have terminated on their own.
        """

        # close sockets and agents
        for colour in Colour:
            x = Protocol.sockets[colour]
            if (len(x.keys()) == 0):
                continue

            try:
                if (kill_children):
                    x['thread'].kill()
                else:
                    x['thread'].wait()
            except Exception as e:
                if (verbose):
                    print(
                        f"Couldn't close {x['name']} " +
                        f"thread. Exception raised: {e}"
                    )

            try:
                x['conn'].close()
                if (verbose):
                    print(
                        f"Closed {x['name']} at {x['addr']}"
                    )
            except Exception:
                if (verbose):
                    print(
                        f"{x['name']} connection was already closed.")

        # close server
        try:
            Protocol.s.close()
        except AttributeError:
            if (verbose):
                print("Socket was not open.")


if __name__ == "__main__":
    commands = [
        "echo Hello 1",
        "echo Hello 2",
        "python agents/NaiveAgent.py"
    ]

    Protocol.start()

    Protocol.accept_connection(commands[2], verbose=True)
    Protocol.accept_connection(commands[2], verbose=True)
    Protocol.send_message(Colour.RED, "START;2;R", verbose=True)
    Protocol.get_message(Colour.RED, verbose=True)
    Protocol.send_message(Colour.BLUE, "START;2;B", verbose=True)
    Protocol.send_message(Colour.RED, "END", verbose=True)
    Protocol.send_message(Colour.BLUE, "END", verbose=True)

    Protocol.close()
