from sys import stderr
from time import time_ns as time
from os.path import realpath, sep
from os.path import exists
from datetime import datetime
from pathlib import Path

from Colour import Colour
from Board import Board
from Move import Move
from Protocol import Protocol
from EndState import EndState


class Game():
    """This class describes a game of Hex."""

    # the maximum time allocated for a match per player
    # 5 minutes in nanoseconds (min * s/min * ns/s)
    MAXIMUM_TIME = 5 * 60 * 10**9
    # 1 second in nanoseconds
    # MAXIMUM_TIME = 10**9

    def __init__(
        self,
        board_size=11,
        player1={
            'name': "Alice",
            "run string": "python3 agents/NaiveAgent.py"
        },
        player2={
            'name': "Bob",
            "run string": "python3 agents/NaiveAgent.py"
        },
        verbose=False,
        log=True,
        print_protocol=False,
        kill_bots=True,
        silent_bots=True
    ):
        self._turn = 1  # current turn count
        self._board = Board(board_size)
        self._player = Colour.RED  # current player
        self._start_time = 0  # used to calculate time elapsed
        self._has_swapped = False  # pie rule

        self._players = {
            Colour.RED: {
                'name': None,
                'run string': None,
                'turns': 0,
                'time': 0
            },
            Colour.BLUE: {
                'name': None,
                'run string': None,
                'turns': 0,
                'time': 0
            }
        }
        self._players[Colour.RED]['name'] = player1['name']
        self._players[Colour.RED]['run string'] = player1['run string']
        self._players[Colour.BLUE]['name'] = player2['name']
        self._players[Colour.BLUE]['run string'] = player2['run string']

        self._kill_bots = kill_bots
        self._silent_bots = silent_bots

        self._verbose = verbose
        self._print_protocol = print_protocol
        self._log = log
        self._start_log()

    def run(self):
        """Runs the match."""
        try:
            self._play()
        except BaseException as e:
            self._end_game(None)
            print(f"Exception raised: {e}")

    def _play(self):
        """Main method for a match.

        The engine will keep sending status messages to agents and
        prompting them for moves until one of the following is met:

        * Win - one of the agents connects their sides of the board.
        * Illegal move - one of the agents sends an illegal message.
        * Timeout - one of the agents fails to send a message before
        the time elapses. This can also be prompted if the agent
        fails to connect.
        """

        # connect to the agents
        self._start_protocol(
            self._players[Colour.RED]['run string'],
            self._players[Colour.RED]['name'],
            self._players[Colour.BLUE]['run string'],
            self._players[Colour.BLUE]['name']
        )
        # test the connection
        if (not self._has_connected):
            self._end_game(EndState.TIMEOUT)
            return

        # start the game
        self._send_message(
            verbose_message=("Started game of Hex. Board is " +
                             f"{self._board.get_size()}x" +
                             f"{self._board.get_size()}."),
            protocol_message=f"START;{self._board.get_size()};",
            start=True
        )

        self._start_time = time()
        end_state = EndState.WIN

        while (not self._board.has_ended()):
            # get a move from the agents
            m, move_time = self._get_move()

            # This message is sent after reading a move because it
            # is a time-consuming operation. Changing the order
            # will decrease the accuracy with which move time is
            # recorded.
            self._send_message(
                verbose_message=self._board.print_board(bnf=False)
            )

            # timeout
            if (move_time == -1):
                end_state = EndState.TIMEOUT
                self._players[self._player]['time'] = Game.MAXIMUM_TIME
                break

            # illegal move
            if (not m.is_valid_move(self)):
                end_state = EndState.BAD_MOVE
                self._flip_turn(move_time)
                break

            # If all checks passed, proceed normally
            self._make_move(m)
            self._flip_turn(move_time)

        self._end_game(end_state)

    def _make_move(self, m):
        """Performs a valid move on the board, then prints its
        results.
        """

        verbose_message = ""  # for the user
        protocol_message = "CHANGE;"  # for the agents

        if (m.is_swap()):
            self._swap()

            verbose_message = "swapped colours"
            protocol_message += "SWAP;"

        else:
            m.move(self._board)

            verbose_message = f"occupied {m.get_x()},{m.get_y()}"
            protocol_message += f"{m.get_x()},{m.get_y()};"

        next_player = self.get_next_player()

        verbose_message = (
            f"{self._players[self._player]['name']} {verbose_message}"
        )
        protocol_message += f"{self._board.print_board()};{next_player}\n"

        self._send_message(verbose_message, protocol_message)

    def get_next_player(self):
        """Returns END if the game is over or the opposite player
        otherwise.
        """

        if (self._board.has_ended()):
            return "END"
        else:
            return self._player.opposite().get_char()

    def _send_message(
        self,
        verbose_message="",
        protocol_message="",
        start=False
    ):
        """Sends messages to the shell or the agents through
        standardised channels. This does not include CSV logging.
        """

        if (self._verbose and verbose_message != ""):
            print(verbose_message)

        if (protocol_message != ""):
            if (start):
                Protocol.send_message(
                    Colour.RED, f"{protocol_message}R\n",
                    verbose=self._print_protocol
                )
                Protocol.send_message(
                    Colour.BLUE, f"{protocol_message}B\n"
                )
            else:
                Protocol.send_message(
                    Colour.RED, protocol_message,
                    verbose=self._print_protocol
                )
                Protocol.send_message(
                    Colour.BLUE, protocol_message
                )

    def _get_move(self):
        """Receives a move from the currently playing agent.

        Returns a tuple (move, time). move is a Move object, and
        time is either an integer representing the time taken in
        nanoseconds, or False if the agent times out. Snapshot
        error is less than 1/100s, but it reflects in the logs.
        The default agent is sometimes too fast to be recorded.
        """

        time_left = Game.MAXIMUM_TIME - self._players[self._player]['time']
        time_left = max(time_left, 0)

        answer, move_time = Protocol.get_message(
            self._player,
            time_left,
            self._print_protocol
        )

        move, log_message = None, 0
        try:
            answer = answer.strip().split(",")
            if (len(answer) == 2):
                # normal move
                x, y = int(answer[0]), int(answer[1])
                log_message = (
                    f"{self._turn}," +
                    f"{self._players[self._player]['name']}," +
                    f"{x},{y},{move_time}"
                )
                move = Move(self._player, x, y)

            elif (answer[0] == "SWAP"):
                # swap move
                log_message = (
                    f"{self._turn}," +
                    f"{self._players[self._player]['name']}," +
                    f"-1,SWAP,{move_time}"
                )
                move = Move(self._player, -1, -1)

            else:
                raise Exception()
        except Exception as e:
            # bad format message
            log_message = (
                f"{self._turn}," +
                f"{self._players[self._player]['name']}," +
                f"-2,{''.join(answer)},{move_time}"
            )
            move = Move(self._player, -2, -2)

        self._write_log(log_message)
        return (move, move_time)

    def _swap(self):
        """Swaps the players' colours in Game and in Protocol."""

        self._players[Colour.RED], self._players[Colour.BLUE] = (
            self._players[Colour.BLUE], self._players[Colour.RED]
        )

        self._has_swapped = True
        self._player = Colour.opposite(self._player)

        Protocol.swap()

    def _flip_turn(self, move_time):
        """Increments the statistics of the current player, then
        changes the current player.
        """

        self._players[self._player]['turns'] += 1
        self._players[self._player]['time'] += move_time

        self._turn += 1
        self._player = Colour.opposite(self._player)

    def _end_game(self, status):
        """Wraps up the game and prints results to shell, log and
        agents.
        """

        # print the board again
        self._send_message(
            verbose_message=self._board.print_board(bnf=False)
        )

        # calculate total time elapsed
        total_time = time() - self._start_time

        # calculate mean move times
        means = {
            'Total': 0,
            Colour.RED: 0,
            Colour.BLUE: 0
        }
        self._turn -= 1  # last move overcounts
        if (self._turn > 0):
            # the real mean move time will be slightly shorter
            means['Total'] = int(total_time / self._turn)
        for colour in Colour:
            if (self._players[colour]['turns'] > 0):
                means[colour] = int(
                    self._players[colour]['time'] /
                    self._players[colour]['turns']
                )

        verbose_message = ""
        protocol_message = "END"
        log_message = ""

        if (status == EndState.WIN):
            # last move overcounts
            self._player = Colour.opposite(self._player)

            verbose_message = (
                f"Game over. {self._players[self._player]['name']} " +
                "has won!\n"
            )
            protocol_message = f"END;{self._player.get_char()}\n"
            log_message = (
                f"0,{self._players[self._player]['name']}," +
                f"End,Win,{self._has_swapped}\n"
            )

        elif (status == EndState.BAD_MOVE):
            # the player printed is the winner
            verbose_message = (
                "Game over. " +
                f"{self._players[self._player.opposite()]['name']} " +
                "has sent an illegal message. " +
                f"{self._players[self._player]['name']} has won!\n"
            )
            protocol_message = f"END;{self._player.get_char()}\n"
            log_message = (
                f"0,{self._players[self._player]['name']}," +
                f"End,Illegal move,{self._has_swapped}\n"
            )

        elif (status == EndState.TIMEOUT):
            # the player printed is the winner
            # last move overcounts
            self._player = self._player.opposite()

            verbose_message = (
                "Game over. " +
                f"{self._players[self._player.opposite()]['name']} " +
                "has timed out. " +
                f"{self._players[self._player]['name']} has won!\n"
            )
            protocol_message = f"END;{self._player.get_char()}\n"
            log_message = (
                f"0,{self._players[self._player]['name']}," +
                f"End,Timeout,{self._has_swapped}\n"
            )

        else:
            # unknown exception raised
            verbose_message = "Game over. It ended abnormally. No winner.\n"
            protocol_message = "END;None\n"
            log_message = "0,None,End,Unknown error\n"

        # total stats
        verbose_message += (
            f"The game took {self._turn} turns and lasted for " +
            f"{Game.ns_to_s(total_time)}s. The mean move time " +
            f"was {Game.ns_to_s(means['Total'])}s.\n"
        )
        log_message += (
            f"0,Total,{self._turn},{total_time},{means['Total']}\n"
        )

        # colour-specific stats
        for colour in Colour:
            verbose_message += (
                f"{self._players[colour]['name']} took " +
                f"{self._players[colour]['turns']} turns in " +
                f"{Game.ns_to_s(self._players[colour]['time'])}s. " +
                "Their average move time was " +
                f"{Game.ns_to_s(means[colour])}s.\n"
            )
            log_message += (
                f"0,{self._players[colour]['name']}," +
                f"{self._players[colour]['turns']}," +
                f"{self._players[colour]['time']},{means[colour]}\n"
            )

        self._send_message(verbose_message, protocol_message)
        self._write_log(log_message)

        if (self._log):
            print(f"Saved log to {self._log_path}")

        # short-form results; easier to read than verbose option
        red_end_s = (str(self._player == Colour.RED) + " " +
                     str(self._players[Colour.RED]['time']) + " " +
                     str(self._players[Colour.RED]['turns']))
        blue_end_s = (str(self._player == Colour.BLUE) + " " +
                      str(self._players[Colour.BLUE]['time']) + " " +
                      str(self._players[Colour.BLUE]['turns']))
        if (self._has_swapped):
            red_end_s, blue_end_s = blue_end_s, red_end_s
        final_message = (
            f"{EndState.get_text(status)}\n{red_end_s}\n{blue_end_s}"
        )
        print(final_message, file=stderr)

        # close communications
        Protocol.close(
            kill_children=self._kill_bots,
            verbose=self._print_protocol
        )

    def _start_protocol(self, s1, name1, s2, name2):
        """Sets up the TCP server, then starts the agents and
        connects to them. If either connection fails, the game
        will not start.
        """
        Protocol.start()

        self._has_connected = Protocol.accept_connection(
            s1, name1, Game.MAXIMUM_TIME,
            self._silent_bots, self._print_protocol
        )
        if (not self._has_connected):
            self._players[Colour.RED]['time'] = Game.MAXIMUM_TIME
            return

        self._has_connected = Protocol.accept_connection(
            s2, name2, Game.MAXIMUM_TIME,
            self._silent_bots, self._print_protocol
        )
        if (not self._has_connected):
            self._players[Colour.BLUE]['time'] = Game.MAXIMUM_TIME
            self._player = self._player.opposite()

    def _start_log(self):
        """Creates the log file and writes the start message."""
        if (not self._log):
            return

        # get the relative path to the log directory
        log_path = realpath(__file__)
        log_path = sep.join(log_path.split(sep)[:-2])
        log_path += f"{sep}logs{sep}"

        # create the log directory if it doesn't exist
        Path(log_path).mkdir(parents=True, exist_ok=True)

        # create a new log file
        self._log_path = log_path + "log.csv"
        idx = 1
        while exists(self._log_path):
            self._log_path = log_path + f"log{idx}.csv"
            idx += 1

        # submit the start message
        with open(self._log_path, "w") as f:
            f.write(f"Start log at {datetime.now()}\n")
            f.write(
                f"Board is {self._board.get_size()}x" +
                f"{self._board.get_size()}.\n"
            )
            f.write("No,Player,X,Y,Time\n")

    def _write_log(self, message):
        """Writes the specified message and a newline to the log file."""
        if (not self._log):
            return

        with open(self._log_path, "a") as f:
            f.write(message + "\n")

    def get_board(self):
        return self._board

    def get_player(self):
        return self._player

    def get_turn(self):
        return self._turn

    @staticmethod
    def ns_to_s(t):
        """Method for standardised nanosecond to second conversion."""
        return int(t/10**6)/10**3


if (__name__ == "__main__"):
    g = Game(board_size=11, verbose=True, mem_eff=True)
    g.run()
