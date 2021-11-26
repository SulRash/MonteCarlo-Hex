# this is expected to throw the same error as TimeoutAgent.
from time import sleep

if (__name__ == "__main__"):
    # I'm not doing anything.
    print("My job here is done.")
    sleep(3)
    print("But I didn't do anything?")
