# File: AdvRoom.py

"""
This module is responsible for modeling a single room in Adventure.
"""

###########################################################################
# Your job for Milestone #1 is to fill in the definitions of the         #
# methods listed in this file, along with any helper methods you need.    #
# The public methods shown in this file are the ones you need for         #
# Milestone #1.  You will need to add other public methods for later      #
# milestones, as described in the handout.  For Milestone #7, you will    #
# need to move the getNextRoom method into the AdvGame class and replace  #
# it with a getPassages method that returns the dictionary of passages.   #
###########################################################################

# Constants

MARKER = "-----"

class AdvRoom:

    def __init__(self, name, shortdesc, longdesc, passages):
        """Creates a new room with the specified attributes."""
        self._name = name
        self._shortdesc = shortdesc
        self._longdesc = longdesc
        self._passages = passages
        self._visited = False
        self._objectNames = [ ]
        #self._objLocation = [ ] # x, y coordinates

    def getName(self):
        """Returns the name of this room.."""
        return self._name

    def getShortDescription(self):
        """Returns a one-line short description of this room.."""
        return self._shortdesc

    def getLongDescription(self):
        """Returns the list of lines describing this room."""
        return self._longdesc

    def setVisited(self, state):
        self._visited = state

    def hasBeenVisited(self):
        return self._visited

    def addObject(self, objname):
        self._objectNames.append(objname)

    def removeObject(self, objname):
        self._objectNames.remove(objname)

    def containsObject(self, objname):
        return objname in self._objectNames

    def getContents(self):
        return self._objectNames

    def getPassages(self):
        return self._passages

    @staticmethod
    def readRoom(f):
        """Reads a room from the data file."""
        roomName = f.readline().rstrip()
        if roomName == "":
            return None
        shortDescription = f.readline().rstrip()
        longDescription = [ ]
        while True:
            line = f.readline().rstrip()
            if line == MARKER: break
            longDescription.append(line)
        passages = [ ]
        while True:
            line = f.readline().rstrip()
            if line == "": break
            colon = line.find(":")
            if colon == -1:
                raise ValueError("Missing colon in " + line)
            passage = line[:colon].strip().upper()
            slash = line.find("/")
            if slash != -1:
                next = line[colon + 1:slash].strip()
                key = line[slash + 1:].strip()
            else:
                next = line[colon + 1:].strip()
                key = None
            passages.append((passage, next, key))
        return AdvRoom(roomName, shortDescription, longDescription, passages)
