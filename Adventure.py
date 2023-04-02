# File: Adventure.py
# ------------------
# This program plays the CS 106AX Adventure game.
# HELP RECEIVED: Jonathan & Jerry's office hours

from AdvGame import AdvGame

# Constants
ADVENTURE_PREFIX = "Hogwarts"

# Main program
def Adventure():
    game = AdvGame(ADVENTURE_PREFIX)
    game.run()

# Startup code
if __name__ == "__main__":
    Adventure()
