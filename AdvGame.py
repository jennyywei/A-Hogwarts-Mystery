# File: AdvGame.py

"""
This module defines the AdvGame class, which records the information
necessary to play a game.
"""

from AdvRoom import AdvRoom
from tokenscanner import TokenScanner
from AdvObject import AdvObject

###########################################################################
# Your job in this assignment is to fill in the definitions of the        #
# methods listed in this file, along with any helper methods you need.    #
# Unless you are implementing extensions, you won't need to add new       #
# public methods (i.e., methods called from other modules), but the       #
# amount of code you need to add is large enough that decomposing it      #
# into helper methods will be essential.                                  #
###########################################################################

class AdvGame:

    def __init__(self, prefix):
        """Reads the game data from files with the specified prefix."""
        self._game = AdvGame.readGame(prefix)
        self._allObjects = AdvGame.readObjects(prefix)
        self._playerObjects = [ ]
        self._synonyms = AdvGame.readSynonyms(prefix)
        self._help = AdvGame.readHelpText()

    def getRoom(self, name):
        """Returns the room with the specified name."""
        return self._game[name]


    def addObjsToRooms(self):
        #Adds all objects to their initial rooms
        for object in self._allObjects.values():
            location = object.getInitialLocation()
            name = object.getName()
            if location != "PLAYER":
                objRoom = self.getRoom(location)
                objRoom.addObject(name)
            else:
                self._playerObjects.append(name)

    def run(self):
        """Plays the adventure game stored in this object."""
        self.addObjsToRooms()
        current = "EntranceHall"
        inMotion = True
        while current != "WIN" or current != "DEATH":
            room = self.getRoom(current)
            if inMotion:
                self.printDescription(room)
                inMotion = False
            actionInput = input("> ").strip().upper()
            scanner = TokenScanner(actionInput)
            scanner.ignoreWhitespace()
            action = self.findSynonyms(scanner.nextToken().upper())
            match action:
                case "QUIT":
                    # current = "EXIT"
                    quit()
                case "HELP":
                    self.help()
                case "LOOK":
                    self.look(room)
                case "TAKE":
                    self.take(room, scanner)
                case "DROP":
                    self.drop(room, scanner)
                case "INVENTORY":
                    self.inventory()
                case "GETCHANGEDROOM":
                    self.getChangedRoom(current)
                case "GETROOMOBJECTS":
                    self.getRoomObjNames(room)
                case _:
                    next = self.getNextRoom(room, action)
                    if next is None:
                        print("I don't know how to apply that word here.")
                    else:
                        current, inMotion = self.returnForced(next)

    def printDescription(self, room):
        # prints the description of a room
        if not room.hasBeenVisited():
            room.setVisited(True)
            for line in room.getLongDescription():
                print(line)
        else:
            print(room.getShortDescription())
        self.printRoomObjects(room)

    def printRoomObjects(self, room):
        # prints the objects in a room
        roomObjects = room.getContents()
        for name in roomObjects:
            description = self._allObjects[name].getDescription()
            if name.find("ROBES") != -1:
                startIndex = description.find("of") + 3
                endIndex = description.find(" ", startIndex)
                primaryColor = description[startIndex:endIndex]
                print("There is " + description + " here. Refer to it as " + primaryColor + "robes.")
            else:
                print("There is " + description + " here.")

    def addToInventory(self, name):
        # adds an object to the player's inventory
        self._playerObjects.append(name)

    def removeFromInventory(self, name):
        # removes an object to the player's inventory
        self._playerObjects.remove(name)

    def isInInventory(self, name):
        # returns a boolean of whether an object is in the player's inventory
        return name in self._playerObjects

    def findSynonyms(self, synonym):
        # returns the synonym of a word that the user inputs, if it exists
        if synonym in self._synonyms:
            return self._synonyms[synonym]
        else:
            return synonym

    def help(self):
        for line in self._help:
            print(line)

    def look(self, room):
        for line in room.getLongDescription():
            print(line)
        self.printRoomObjects(room)

    def take(self, room, scanner):
        objName = self.findSynonyms(scanner.nextToken().upper())
        if objName == "":
            print("You must specify what to take.")
        elif objName == "ROBES":
            print("You must specify which color robes to take.")
        elif room.containsObject(objName):
            room.removeObject(objName)
            self.addToInventory(objName)
            print("Taken.")
        elif objName not in self._allObjects:
            print("I don't know what that is.")
        else:
            print("I do not see that here.")

    def drop(self, room, scanner):
        objName = self.findSynonyms(scanner.nextToken().upper())
        if objName == "":
            print("You must specify what to drop.")
        elif objName == "robes":
            print("You must specify which set of robes to drop.")
        elif objName not in self._allObjects:
            print("I don't know what that is.")
        elif objName not in self._playerObjects:
            description = self._allObjects[objName].getDescription()
            print("You are not holding " + description + ".")
        else:
            room.addObject(objName)
            self.removeFromInventory(objName)
            print("Dropped.")

    def inventory(self):
        if len(self._playerObjects) == 0:
            print("You are empty-handed.")
        else:
            print("You are carrying:")
            for name in self._playerObjects:
                print("\t" + self._allObjects[name].getDescription())

    def getChangedRoom(self, roomName):
        print(roomName)

    def getRoomObjNames(self, room):
        output = ""
        roomObjects = room.getContents()
        for name in roomObjects:
            output += name + " "
        output = output.strip()
        print(output)

    def getNextRoom(self, room, verb):
        """Returns the name of the destination room after applying verb."""
        next = None
        passages = room.getPassages()
        for passage in passages:
            if passage[0] == verb:
                key = passage[2]
                if self.isInInventory(key) or key is None:
                    next = passage[1]
                    return next
        if next is None:
            for passage in passages:
                if passage[0] == "*" and verb != "FORCED":
                    next = passage[1]
                    break
        return next

    def returnForced(self, currRoomName):
        """ returns the final room that the player arrives at after implementing forced motion
            also returns a boolean representing if the player is inMotion
        """
        FORCE = "FORCED"
        currRoom = self.getRoom(currRoomName)
        next = self.getNextRoom(currRoom, FORCE)
        if next is None: return currRoomName, True
        while self.getNextRoom(currRoom, FORCE) is not None:
            next = self.getNextRoom(currRoom, FORCE)
            for line in currRoom.getLongDescription():
                print(line)
            if next == "EXIT": return next, False
            currRoom = self.getRoom(next)
        if currRoom.hasBeenVisited():
            return next, False
        return next, True

    @staticmethod
    def readGame(filename):
        with open(filename + "Rooms.txt") as f:
            rooms = { }
            while True:
                room = AdvRoom.readRoom(f)
                if room is None: break
                name = room.getName()
                rooms[name] = room
        return rooms

    @staticmethod
    def readObjects(filename):
        objects = { }
        try:
            with open(filename + "Objects.txt") as f:
                while True:
                    object = AdvObject.readObject(f)
                    if object is None: break
                    name = object.getName()
                    objects[name] = object
                return objects
        except IOError:
            return objects

    @staticmethod
    def readSynonyms(filename):
        synonyms = { }
        try:
            with open(filename + "Synonyms.txt") as f:
                while True:
                    line = f.readline().rstrip()
                    if line == "": break
                    sep = line.find("=")
                    if sep == -1:
                        raise ValueError("Missing separator in " + line)
                    synonym = line[:sep].strip().upper()
                    definition = line[sep + 1:].strip()
                    synonyms[synonym] = definition
                return synonyms
        except IOError:
            return synonyms

    @staticmethod
    def readHelpText():
        with open("HelpText.txt") as f:
            lines = f.read().splitlines()
            return lines