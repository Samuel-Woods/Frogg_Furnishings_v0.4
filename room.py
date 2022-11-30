import graphics as g

# rooms should have graphics, but it should be in grey
# if you're giving rooms colours, objects may as well have them too, and players could really use it

# Collection of all rooms
rooms_list = []


# def_fn is a function that determines whether a given point is in the room
# Priority determines how important a room's properties are. any getRoom functions take the room with highest priority
# That way multiple rooms can sit on top of each other
class Room:
    def __init__(self, name, description, def_fn, priority=3, image=None):
        self.name = name  # Might not be necessary
        self.description = description
        self.objects = []  # Might not be necessary
        self.image = ["     ", "     ", "     "] if image is None else image
        self.def_fn = def_fn
        self.priority = priority
        rooms_list.append(self)
        # list of coordinates within the room
        # a function that defines what's in the room? or a list of conditions?

    # returns True iff given coordinates meet the function of the room
    # This also means you could have multiple rooms in the same place??
    def isInRoom(self, x, y):
        return True if self.def_fn(x, y) else False


def getRoomAt(x, y):
    current_room = null_room
    for room in rooms_list:
        if room.def_fn(x, y) and room.priority > current_room.priority:
            current_room = room
    return current_room


def nullRoomDef(x, y):
    return True
null_room = Room("Ultima", "You are surrounded by green foam.", nullRoomDef, 0, ["     ", "     ", "     "])


def froggFurnishingsDef(x, y):
    if -9 <= x <= 12 and -4 <= y <= 10:
        return True
    return False
frogg_furnishings = Room("Frogg Furnishings", "The greatest furniture store on Gearth!", froggFurnishingsDef, 3)
