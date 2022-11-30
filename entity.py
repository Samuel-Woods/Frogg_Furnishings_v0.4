import graphics as g
import room as r
import random

# this function might belong in room
def dirToCoords(direction):
    # X is right, Y is up
    # 0  1  2  3  ==>  y+1 x+1 y-1 x-1
    direction_coords = [0, 0]
    if direction % 2 == 0:
        direction_coords[1] = 1 if direction == 0 else -1
    else:
        direction_coords[0] = 1 if direction == 1 else -1
    return direction_coords


entities_list = []
entities_list_without_walls = []
objects_list = []
objects_list_without_walls = []
# Walls list works a bit differently because it's organised
walls_list = []


# Checks if there is an entity at (x, y). this function doesn't need to be in the entity class, necessarily?
def isEntityAt(x, y, allowed_entities=None, ignore_collisionless=False):
    if allowed_entities is None:
        allowed_entities = entities_list
    for entity in allowed_entities:
        if entity.x == x and entity.y == y:
            if ignore_collisionless and entity.collisionless:
                pass
            else:
                return True
    return False


def getEntityAt(x, y, allowed_entities=None):
    if allowed_entities is None:
        allowed_entities = entities_list
    for entity in allowed_entities:
        if entity.x == x and entity.y == y:
            return entity
    return null_entity


def getNearestOpenTile(x, y, algorithm="diamond"):
    # Check for search range 0
    tiles_checked = 2  # for "prime spiral" algorithm
    if not isEntityAt(x, y):
        return [x, y]
    search_range = 1
    while True:
        if algorithm == "square":
            x_lower_lim = x - search_range
            x_upper_lim = x + search_range
            y_lower_lim = y - search_range
            y_upper_lim = y + search_range
            for search_y in range(y_upper_lim, y_lower_lim - 1, -1):
                for search_x in range(x_lower_lim, x_upper_lim + 1):
                    if not isEntityAt(search_x, search_y):
                        return [search_x, search_y]
        elif algorithm == "diamond":
            # Searching in a diamond spiral shape, going clockwise
            for diamond_edge in range(4):
                for tile_to_search in range(search_range):  # from 0 to search_range - 1
                    coords_to_check = [  # top left edge: start at -X corner, move +X/+Y
                        [x - search_range + tile_to_search, y + tile_to_search],
                        # top right edge: start at +Y corner, move +X/-Y
                        [x + tile_to_search, y + search_range - tile_to_search],
                        # bot right edge: start at +X corner, move -X/-Y
                        [x + search_range - tile_to_search, y - tile_to_search],
                        # bot left edge: start at -Y corner, move -X/+Y
                        [x - tile_to_search, y - search_range + tile_to_search]]
                    if not isEntityAt(coords_to_check[diamond_edge][0], coords_to_check[diamond_edge][1]):
                        return coords_to_check[diamond_edge]
        # look up other interesting step functions
        # this could be merged with the diamond part, since the only difference is what coords_to_check is
        elif "spiral" in algorithm:
            for square_edge in range(4):
                for tile_to_search in range(search_range * 2):
                    coords_to_check = [# top edge: start at -X/+Y corner, move +X
                        [x - search_range + 1 + tile_to_search, y + search_range],
                                       # right edge: start at +X/+Y corner, move -Y
                        [x + search_range, y + search_range - 1 - tile_to_search],
                                       # bot edge: start at +X/-Y corner, move -X
                        [x + search_range - 1 - tile_to_search, y - search_range],
                                       # left edge: start at -X/-Y corner, move +Y
                        [x - search_range, y - search_range + 1 + tile_to_search]]
                    if not isEntityAt(coords_to_check[square_edge][0], coords_to_check[square_edge][1]):
                        if "prime" not in algorithm:
                            return coords_to_check[square_edge]
                        # THE FOLLOWING IS A PRIMENESS ALGORITHM.
                        elif tiles_checked == 1:
                            pass
                        else:
                            tiles_checked_prime = True
                            for n_to_check in range(2, tiles_checked):
                                if tiles_checked % n_to_check == 0:
                                    tiles_checked_prime = False
                            if tiles_checked_prime:
                                return coords_to_check[square_edge]
                    tiles_checked += 1
        search_range += 1


class Entity:
    def __init__(self, name, x, y, description, image):
        self.x = x
        self.y = y
        self.description = description
        self.name = name
        self.image = image
        entities_list.append(self)
        entities_list_without_walls.append(self)

    def getRoom(self):
        return r.getRoomAt(self.x, self.y)

    def move(self, x, y):
        if not isEntityAt(x, y):
            self.x = x
            self.y = y
            return True
        return False

    # If this causes bugs, just use dist to entity owner
    def distToEntity(self, entity):
        dist_to_entity = abs(self.x - entity.x) + abs(self.y - entity.y)
        dist_to_entity_owner = abs(self.x - entity.item.owner.x) + abs(self.y - entity.item.owner.y)
        return min(dist_to_entity, dist_to_entity_owner)

    def getCoordsInDir(self, direction, distance=1):
        coords_in_dir = [self.x, self.y]
        for step in range(distance):
            coords_in_dir[0] += dirToCoords(direction)[0]
            coords_in_dir[1] += dirToCoords(direction)[1]
        return coords_in_dir

    def findDirectionTo(self, x, y, allow_blocks=False):
        dist_to_point = abs(self.x - x) + abs(self.y - y)
        possible_directions = []
        for direction in range(4):
            x_in_direction = self.getCoordsInDir(direction)[0]
            y_in_direction = self.getCoordsInDir(direction)[1]
            if abs(x_in_direction - x) + abs(y_in_direction - y) < dist_to_point:
                if allow_blocks or getEntityAt(x_in_direction, y_in_direction) == null_entity:
                    possible_directions.append(direction)
        if len(possible_directions) == 0:
            return random.choice([0, 1, 2, 3])
        return random.choice(possible_directions)

    # Hopefully less laggy version, so I don't have to check every single entity
    # This function calls getEntityAt, which uses the entity list, so this doesn't actually help yet
    # Still, very nice for a lot of other situations
    def getEntitiesInRange(self, entity_range, allowed_entities=None):
        if allowed_entities is None:
            allowed_entities = entities_list
        entities_in_range = []
        for rangecheck_x in range(self.x - entity_range, self.x + entity_range + 1):
            for rangecheck_y in range(self.y - entity_range, self.y + entity_range + 1):
                if isEntityAt(rangecheck_x, rangecheck_y, allowed_entities):
                    entities_in_range.append(getEntityAt(rangecheck_x, rangecheck_y))
        return entities_in_range

    # Sends a sound to every entity in range. Only NPCs do anything when they receive it.
    def sound(self, message, sound_range=4):
        entities_in_range = self.getEntitiesInRange(sound_range)
        for entity_in_range in entities_in_range:
            entity_in_range.receiveSound(message)

    # Placeholder function so the program doesn't crash when an object receives a sound
    def receiveSound(self, message):
        pass

    # Teleports the entity to the nearest unoccupied space
    # Could very possibly be used to escape the map
    def unstuck(self):
        unstuck_tp_coords = getNearestOpenTile(self.x, self.y)
        self.move(unstuck_tp_coords[0], unstuck_tp_coords[1])

    # PUSH
    # Doesn't account for special object properties yet
    def push(self, direction):
        # get entity in direction
        if isEntityAt(self.getCoordsInDir(direction)[0], self.getCoordsInDir(direction)[1], entities_list_without_walls):
            entity_to_push = getEntityAt(self.getCoordsInDir(direction)[0], self.getCoordsInDir(direction)[1], entities_list_without_walls)
        else:
            return False
        # Get push destinations
        push_destination_x = entity_to_push.getCoordsInDir(direction)[0]
        push_destination_y = entity_to_push.getCoordsInDir(direction)[1]
        # Check if something's there
        push_blocked = isEntityAt(push_destination_x, push_destination_y)
        if push_blocked:
            return False
        if entity_to_push.move(push_destination_x, push_destination_y):
            return True
        return False


null_entity = Entity(" ", -1000, -1000, " ", g.blank_image)


class Item:
    def __init__(self, object_stored, owner):
        self.object_stored = object_stored
        self.owner = owner
        self.x = owner.x
        self.y = owner.y


# Different object properties could potentially be classes. Or maybe individual objects.
class Object(Entity):
    def __init__(self, name, x, y, properties, description, image, item_name="", interact_message="", use_message="", value=""):
        # From Entity
        self.x = x
        self.y = y
        self.description = description
        self.name = name
        self.item_name = name.split()[-1][0:10] if item_name == "" else item_name  # first 10 letters of last word of name. can be set to other stuff if needed
        self.image = image
        entities_list.append(self)
        entities_list_without_walls.append(self)
        # Object-specific
        self.properties = properties
        self.interact_message = interact_message
        self.use_message = use_message
        self.value = value
        self.item = Item(self, self)
        objects_list.append(self)
        objects_list_without_walls.append(self)

    def move(self, x, y):
        if "pushable" in self.properties:
            self.x = x
            self.y = y
            self.item.x = x
            self.item.y = y
            return True
        return False


# Properties list:
# "pushable": can be pushed by players
# "obtainable": can be picked up by players as an item
# "frogly", "very frogly", "extremely frogly": grants 1, 2 or 3 froglyness while in inventory
# "indignified": grants 1 indignity while in inventory
# "dignified": removes 1 indignity while in inventory
# "frogly/indig/dignified food": +1 to that stat on eating. doesn't stack with normal version or property
# ""
# "messy": breaks on throw??
# "edible": eats on Use (if frogly or indignified, you gain the froglyness but also lose it for consuming the item)
# For 'get on push' items, just give them Obtainable but not Pushable
# obt but not push ==> get on push
# push but not obt ==> sokoban puzzle (but with furniture haha)


# OBJECT INITIALISATION

# ULTIMA OBJECTS
# Pgenobj doesn't go to ultima when picked up, so it *always* has null properties
# it's also very frogly, so it gives you a free 6 froglyness, making frog teleportation easy
# I guess it also defines a natural 'spawn point' in the overworld
pgenobj = Object("Perfectly Generic Object", 413, 612, ["pushable", "obtainable", "null", "very frogly"], "[Null] [Frogly +2] A large, lightly beveled cube made from green foam. You're sure it could be more generic, but you can't figure out how.", ["┌───┐", "│   │", "└───┘"], "GenericObj")


# FROGG FURNISHINGS OBJECTS
# Bakery + Kitchen
bug_pie = Object("Cinnamon Bug Pie", -3, 10, ["66", "pushable", "obtainable", "edible X3", "buy", "messy throw", "indignity on hit", "cinnamon bugs on hit"],
                 "[Buy 50ZM] [Edible X3] [Splat] A delicious three-course cinnamon bug pie!", [" /%\ ", " %%% ", " \%/ "])
indignified_tart = Object("Indignified Tart", -5, 7, ["pushable", "obtainable", "edible", "indignified food", "break on throw", "indignity on hit"],
                          "[Edible (+1 indig)] [Splat] This tart has a jam swastika carved into the pastry. You wouldn't want to be caught eating it.", ["     ", "  ^  ", " \#/ "])
meat_cake = Object("Meat Cake", -5, 9, ["pushable", "obtainable", "edible", "messy throw", "indignity on hit"],
                   "[Edible] [Splat] A red spongecake with huge slabs of meat in between the layers. The perfect mix of meat and candy.",
                   ["  i  ", " _%%_", " ≈≈≈≈"])
swastika_badge = Object("Swastika Badge", 0, 10, ["2", "pushable", "obtainable", "indignified", "swastika", "clothing", "rank on use", "can repeat rank", "indignity on hit"],
                        "[Indig] [+1 indig throw] This badge has a swastika on it.", ["     ", " (X) ", "     "], "Nazi Badge")
corpse = Object("Corpse", -1, -9, ["pushable", "obtainable", "edible", "indignified", "very indignified food"],
                "[Indig] [Edible (+2 indig)] A disturbingly fresh dead body. Someone has hacked its chest open and taken out all the organs.", [" |  /", "O### ", " |  \\"])
# Kolunu Den + Storage
radio = Object("radio", 4, 9, ["pushable", "obtainable"], "An AM radio. It seems to be saying something important.",
               ["     ", " \ / ", "[≡≡≡]"])
kolunu_deed = Object("Kolunu Deed", 5, 9, ["pushable", "obtainable", "kolunu deed"],
                     "Wherever the deed goes, Mr Kolunu will follow.", [" ┌─┐ ", " │K│ ", " └▒┘ "])
one_mans_trash = Object("One Man's Trash", 9, 6, ["66", "pushable", "zorkmids on interact"],
                        "A pile pf old junk. Hopfully they won't mind if you root through it.", ["  %  ", " Θ$# ", "%&&≡#"])
kolunu_crackers = Object("Kolunu Crackers", 9, 5, ["pushable", "obtainable", "edible"],
                         "[Edible] These don't belong to you. Give them back.", ["     ", "  %  ", "     "])
# Bathroom + Sitting room
sink = Object("Bathroom Sink", -7, 4, ["pushable", "obtainable", "vomit bag on interact", "text on use"],
              "[Vomit interact] This is the bowl for hand-washing. DO NOT WASH YOUR HANDS IN THE OTHER BOWL.",
              ["     ", " \≈/ ", "  ║  "], "Sink", "", "You turn the tap on, trickling water behind you.")
toilet1 = Object("Toilet", -9, 3, ["pushable", "obtainable", "vomit bag on interact", "sound on use"],
                 "[Vomit interact] You don't think this toilet is properly attached to the waterworks.", ["-]   ", "[===]", " \_/ "],
                 "Toilet", "", "flushes the toilet. *FLUSHHH*.")
beanbag1 = Object("Beanbag", 1, 5, ["obtainable", "pushable"], "Like a chair, but comfier.", ["     ", "     ", "(###)"])
chair1 = Object("Wooden Chair", -5, 5, ["obtainable", "pushable"], "A sturdy but uncomfortable wooden chair.", [" │   ", " ├─┐ ", " │ │ "])
ornate_table = Object("Ornate Table", -1, 4, ["obtainable", "pushable"], "An antique wooden table.", ["     ", "*═*═*", "│   │"])
sofa1 = Object("Sofa", -2, 3, ["pushable", "obtainable"], "A comfy red sofa.", ["     ", "|---|", "|===|"])
# Two East rooms
dignified_hat = Object("Dignified Hat", 5, 5,
                       ["pushable", "obtainable", "dignified", "clothing", "text on interact"], "[Dignity +1] A classy fedora.", ["     ", "_/=\_", "     "], "Dignf Hat",
                       "You push the top of the hat through the bottom so it's inside out. Nobody is any the wiser, except for perhaps people with eyes.")
frogly_shirt = Object("Frogly Shirt", 6, 3, ["pushable", "obtainable", "frogly", "clothing", "drop on use"],
                      "[Frogly +1] A green T-shirt with 'STAY FROGLY!' written on the front.", ["//---", ")frog", "\\\---"], "F-Shirt")
fishing_fnome = Object("Fisherfnome", 3, 3, ["very frogly", "pushable", "obtainable"],
                       "[Frogly +2] A model frog holding a fishing pole in front of him. His name is easily unpronounced.", ["<<:) ", " /   ", "/---o"], "Fishfnome")
marbles1 = Object("Marbles", 6, -1, ["obtainable", "text on interact", "throw on use"], "Don't slip on them! (Use to throw.)",
                  ["∙    ", "   * ", " o   "], "Marbles", "You roll the marbles around aimlessly.")
marbles2 = Object("Marbles", 7, -1, ["obtainable", "text on interact", "throw on use"], "Don't slip on them! (Use to throw.)",
                  ["∙    ", "   * ", " o   "], "Marbles", "You roll the marbles around aimlessly.")
# Pond
ribbit_stall = Object("Ribbit Stall", -5, 1, ["pushable", "frogly", "text on interact"],
                      "A wooden counter, with 'RIBBING LESSONS - 20 ZORKMIDS EACH' written on the front.", ["|   |", "O═══O", "│RIB│"], "Rib Stall",
                      "RIBBIT STALL: Talk to Mr Frog for more details. You must have prior experience with ribbing.")
fnome = Object("Fnome", -6, -1, ["pushable", "obtainable", "frogly"], "[Frogly +1] A painted ceramic model of a frog, with a red hat and a beard. His name is easily mispronounced.", ["     ", " <:) ", "     "])
nuld = Object("Nuld", 5, -3, ["pushable", "obtainable"], "This is a nuld. Everyone knows what nulds are.", ["  n  ", " nNn ", "  n  "])
dung_boulder = Object("Dung Boulder", -4, 5, ["pushable", "smelly"], "A massive ball of dung. It would be a shame to find one of these blocking your front door.", ["*%&%*", "%&#&%", "*%&%*"])
watch = Object("Pocket Watch", -9, 4,  ["obtainable"], "This watch tells the time like it is.", ["     ", "=[o]=", "     "])
bug = Object("Bug", 5, 1, ["pushable", "obtainable", "edible", "frogly food"], "A bug! Eat it!", ["     ", "  *  ", "     "])
two_headed_fnome = Object("Two-headed Fnome", 10, -2, ["pushable", "obtainable", "very frogly"], "Twice the heads ==> twice the hats ==> twice the froglyness.", ["     ", "<:)┐#", "<:)┘#"], "Fnome X2")
slingshot = Object("Slingshot", 10, 0, ["pushable", "obtainable", "throw last item on use"], "The tool of a master prankster. Hold use to agitate the last item in your sylladex.", ["     ", " \___", " /   "])
broken_tv = Object("Broken TV", 11, -2, ["pushable", "obtainable"], "If only you could find the remote.", [" \ / ", "┌▒░░┐", "└───┘"])
grilk_bottle = Object("Grilk", 11, 1, ["pushable", "obtainable", "edible", "frogly", "frogly food"], "It's what cows drink.",  ["     ", ">[==]", "     "])

def objectActions():
    # Slingshot
    if "going slack" in slingshot.properties:
        slingshot.properties.remove("going slack")
        slingshot.properties.remove("pulled back")
    if "pulled back" in slingshot.properties:
        slingshot.properties.append("going slack")
    # Radio
    if g.turn_count % 2 == 0:
        radio.item.owner.sound("RADIO: " + radio_script[(g.turn_count // 2) % len(radio_script)], 1)
    # Pocket Watch
    watch.item.owner.feedback = f"The time is {g.sorfTime()}"


radio_script = ["Message repeats.", "This is an urgent message for MR KOLUNU.",
                "We need you to break in and steal", "MR SWASTIKA'S CINNAMON BUG PIE.",
                "Bring the pie to the MOST FROGLY PLACE", "for further instructions.", "*crackles*",
                "We now return to our regularly scheduled program.", "*crackles*",
                "As conceived in 1632 by Portuguese printing press operator Andre Filipe,",
                "boxing was a gentlemen’s game in which two men would square off",
                "and regale each other with stories monotonous for days on end",
                "until one of them fell to the ground from boredom or exhaustion.", "*crackles*",
                "Over the next few years, the new sport developed",
                "a respectable following of a few hundred local socialites.",
                "It was Filipe’s son, Andre Filipe Filipe,",
                "who developed what he called 'the punching strategy'",
                "in 1637 after seeing a schoolboy strike another in anger, causing him to fall down.", "*crackles*",
                "When Andre Filipe Filipe challenged the then-champion, British ex-patriate",
                "“Sleepless” Bill Bishop to a match, Bishop was the odds-on favourite.",
                "You can imagine his surprise when while he was describing what he had",
                "had for breakfast that morning, Andre walked up and thumped him in the neck,",
                "sending him down “for the count” in the parlance of our time.",
                "*crackles*", "While it was universally agreed that",
                "the boy had violated the spirit of the game,",
                "officials were unable to find any actual rule that",
                "punching violated, and were forced to let the victory stand.",
                "*crackles*", "This upset caused an uproar in the boxing community",
                "large enough to spill over into local newspapers,",
                "and stirred the interest of many outsiders to come see what the fuss was about.",
                "The newcomers were enthralled to engage in these borderline",
                "barbaric displays of human strength and skill, and the rest is history.",
                "– after a few spoilsport schoolmarms single-minded about safety",
                "added the padded gloves, of course.", "*crackles*",
                "Today’s boxing enthusiasts fantasise about the newcomer",
                "that would rock the ring the way Filipe did.",
                "Classification of the modern ruleset has essentially locked the",
                "punching strategy into place; but it’s easy to get caught up in the fantasy.",
                "Young scholars with big dreams often enter the ring",
                "with their crazy new trick, usually a variant of hypnosis.",
                "And though they’ve achieved the occasional victory, none of",
                "the gimmicks have been robust enough to make it to the big-time.", "*crackles*",
                "The real wonder, though, is that Andre",
                "Filipe’s original vision of boxing is still around.",
                "Gentlemen’s boxing clubs can be found in cities all over the world;",
                "you can visit one most any day of the week and see",
                "two erudite gentlemen exchanging pleasantries in the ring.",
                "Most people only come to watch a few hours of a match, and then leave.",
                "But every once in a while you’ll find amongst your elders a stout fellow,",
                "a die-hard fan, who perhaps witnessed that historic battle between Filipe and Bishop,",
                "who for love of the sport must stay to witness",
                "the last glorious seconds of wakefulness slip away,",
                "only to return to fight again another day.", "*crackles*", "*crackles*", "*crackles*", "*crackles*",
                "*crackles*", "*crackles*", "*crackles*", "*crackles*", "*crackles*", "*crackles*", "*crackles*"]
