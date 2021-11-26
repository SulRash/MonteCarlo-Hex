"""This script runs one game of Hex.

This is effectively what starts the game. This script may work when run
directly, with the same specification as Hex.py, but it is not recommended.
"""
from sys import argv, platform
from os.path import realpath, sep

from Game import Game


def main():
    verbose = ("-v" in argv or "-verbose" in argv)
    log = ("-l" in argv or "-log" in argv)
    print_protocol = ("-p" in argv or "-print_protocol" in argv)
    kill_bots = ("-k" in argv or "-kill_bots" in argv)
    silent_bots = ("-sb" in argv or "-silent_bots" in argv)
    java_ref_agent = ("-j" in argv or "-java" in argv)
    double = ("-d" in argv or "-double" in argv)

    board_size = 11
    agents = []

    for argument in argv:
        if ("agent=" in argument or "a=" in argument):
            agents.append(argument)
        if ("board_size=" in argument or "b=" in argument):
            try:
                board_size = int(argument.split("=")[1])
                if (board_size < 1):
                    raise Exception("Board size too small.")
            except Exception as e:
                print(
                    "ERROR: Board size argument is not in valid",
                    "format. Aborted."
                )
                return

    if (len(agents) > 2):
        print("ERROR: Too many agents specified. Aborted.")
        return
    elif (len(agents) < 2):
        if (len(agents) == 1 and double):
            print("NOTICE: Double agent enabled. Your agent will play both sides.")
            try:
                agent1 = {
                    "name": agents[0].split(";")[0].split("=")[1],
                    "run string": agents[0].split(";")[1]
                }
            except Exception as e:
                print("ERROR: Agent arguments not valid. Aborted")
                return
            
            agents.append(f"a={agent1['name']}1;{agent1['run string']}")

        else:
            print(
                "NOTICE: Fewer than two agents specified.",
                "Missing players will be replaced with the default agent."
            )

            if (not java_ref_agent):
                cmd_ending = "3"
                if (platform == "win32"):
                    cmd_ending = ""

                # watch out -- literal
                agent_path = sep.join(realpath(__file__).split(sep)[:-2])
                agent_path += f"{sep}agents{sep}DefaultAgents{sep}NaiveAgent.py"
                agent_cmd = f"python{cmd_ending} {agent_path}"

            else:
                print("NOTICE: Java reference agent was selected.")
                agent_dir = sep.join(realpath(__file__).split(sep)[:-2])
                agent_dir += f"{sep}agents{sep}DefaultAgents"
                agent_cmd = f"java -classpath {agent_dir} NaiveAgent"

            
            for idx in range(2-len(agents)):
                agent_string = f"agent=DefaultAgent{idx+1};{agent_cmd}"
                agents.append(agent_string)

    try:
        player1 = {
            "name": agents[0].split(";")[0].split("=")[1],
            "run string": agents[0].split(";")[1]
        }
        player2 = {
            "name": agents[1].split(";")[0].split("=")[1],
            "run string": agents[1].split(";")[1]
        }
    except Exception as e:
        print("ERROR: Agent arguments not valid. Aborted")
        return
    if ("-switch" in argv or "-s" in argv):
        player1, player2 = player2, player1

    g = Game(
        board_size=board_size,
        player1=player1, player2=player2,
        verbose=verbose,
        log=log,
        print_protocol=print_protocol,
        kill_bots=kill_bots,
        silent_bots=silent_bots
    )
    g.run()


if __name__ == "__main__":
    main()
