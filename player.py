import graphics as g
import room as r
import entity as e
import random

creatures_list = []
players_list = []
npcs_list = []
frogs_list = []

rank_titles = ["0: TADPOLE TYKESPRITE", "I: FLEDGLING FROGSPAWN", "II: HITLER SUPPORTER", "III: THE ONE WHO WAS RIGHT", "IV: GOTTA PIE",
               "V: WHO WAS THAT GUY?", "VI: THANK YOU GREAT FISH", "VII: JUST GRILKIN'", "VIII: BIGMOTH STRIKER", "IX:"
               "X: NAPPY KID", "XI: PHLEGM SMELLER", "XII: BOTTOM BLARTER", "XIII: GOTTA ABSCOND, BRO!", "XIV: RIBBIT RUSTLER",
               "XV: BUG EATER GENERAL", "XVI: FORG TO THE FJORD"]
# add more alliterative frog ranks. HOPFUL HUSTLER. LILYPAD LACKADAISER. AGRRIEVING AMPHIBIAN. UNTOOTHED TURNABOUT.
# ix could be cowabunger, if I can figure out what cowabunger is
# low - cowabunger, beloved family nft, gotta abscond, bro!
# med - ribbit rustler, straight wumping, crown vomitorious, oh, i get it, golfer? i hardly knew her! (for sokoban golf)
# high - top ssg runner, legendary piece of trash, frogety bopper, vast croaker

ribtionary = {
    "ribbit": 7,    # more messages unlocked
    "kerchom": 6,   # eat big bugs? long-range tongue?
    "frog hop": 5,  # dance
    "croak": 4,     # more messages unlocked, more replies unlocked
    "eat bugs": 3,  #
    "lilypad": 2,   # sit on a lilypad  # maybe sitting on a lilypad lets you move across water :))
    "rib": 2,       # more messages unlocked, more replies unlocked
    "talk to frogs": 1,     # you talk in broken froglish. frogs might charge you move
    "talk to anyone": -1000,
    "speak": -1000}         # low frogly ==> indignified npcs kinder to you


class Creature(e.Entity):
    def __init__(self, name, x, y, description, image, zorkmids, indignity, froglyness):
        # From Entity
        self.x = x
        self.y = y
        self.description = description
        self.name = name
        self.image = image
        e.entities_list.append(self)
        e.entities_list_without_walls.append(self)
        # Creature-specific
        self.facing = 0
        self.inventory = []
        self.zorkmids = zorkmids
        self.indignity = indignity
        self.indignity_threshold = 3
        self.froglyness = froglyness
        self.turns_until_frog_tp = 10
        self.feedback = ""
        self.recent_events = [""]
        creatures_list.append(self)

    def receiveSound(self, message):
        self.recent_events.append(message)

    def objGetProperties(self, object_to_get):
        if "buy" in object_to_get.properties:
            self.zorkmids -= int(object_to_get.properties[0])
            object_to_get.properties.remove("buy")
        if "frogly" in object_to_get.properties:
            self.froglyness += 1
        if "very frogly" in object_to_get.properties:
            self.froglyness += 2
        if "extremely frogly" in object_to_get.properties:
            self.froglyness += 3
        if "indignified" in object_to_get.properties:
            self.indignity += 1
        if "dignified" in object_to_get.properties:
            self.indignity_threshold += 1
        if "swastika" in object_to_get.properties:
            if isinstance(self, Player):
                if 2 not in self.ranks_achieved:
                    self.climbRank(2)
        if "clothing" in object_to_get.properties:
            self.description += f" They are wearing a {object_to_get.name}."

    def objDropProperties(self, object_to_drop):
        drop_coords = self.getCoordsInDir(self.facing)
        entity_at_drop = e.getEntityAt(drop_coords[0], drop_coords[1])
        giving_to_creature = True if entity_at_drop in creatures_list else False
        if giving_to_creature and "sell" in object_to_drop.properties:
            # This bit of code can force people into debt, so shouldn't exist.
            sell_value = int(object_to_drop.properties[0])
            self.zorkmids += sell_value
            entity_at_drop.zorkmids -= sell_value
            object_to_drop.properties.remove("sell")
        if "frogly" in object_to_drop.properties:
            self.froglyness -= 1
        if "very frogly" in object_to_drop.properties:
            self.froglyness -= 2
        if "extremely frogly" in object_to_drop.properties:
            self.froglyness -= 3
        if "indignified" in object_to_drop.properties:
            self.indignity -= 1
        if "dignified" in object_to_drop.properties:
            self.indignity_threshold -= 1
        if "clothing" in object_to_drop.properties:
            desc_to_remove = f"They are wearing a {object_to_drop.name}"
            self.description = g.removeSentence(self.description, desc_to_remove)  # second arg must be missing full stop to work

    def objThrowProperties(self, object_to_throw):
        if "messy" in object_to_throw.properties:
            pass
        if "splat on throw" in object_to_throw.properties:

            pass

    def move(self, x, y):
        move_blocked = e.isEntityAt(x, y)
        # if would move into an impassable room (eg water), movement is blocked
        if not move_blocked:
            self.x = x
            self.y = y
            for item in self.inventory:
                item.x = self.x
                item.y = self.y
            return True
        return False

    def get(self, object_to_get):
        object_to_get.item.owner = self
        object_to_get.item.x = self.x
        object_to_get.item.y = self.y
        self.inventory.insert(0, object_to_get.item)
        # Send object to Ultima
        if "null" not in object_to_get.properties:
            get_tp_coords = e.getNearestOpenTile(413, 612, "prime spiral")
            object_to_get.x = get_tp_coords[0]
            object_to_get.y = get_tp_coords[1]
            object_to_get.sound(f"{object_to_get.name} appears in a flash of green light!")
        self.feedback = f"You got the {object_to_get.name}."
        # Throw if inv full
        if len(self.inventory) > 3:
            self.feedback = f"Your sylladex is overloaded! It spits out the {self.inventory[-1].object_stored.name}."
            self.throw(-1)
        self.objGetProperties(object_to_get)
        return True

    def attemptGet(self):
        get_x = self.getCoordsInDir(self.facing)[0]
        get_y = self.getCoordsInDir(self.facing)[1]
        if not e.isEntityAt(get_x, get_y):
            return False
        object_to_get = e.getEntityAt(get_x, get_y)
        if object_to_get not in e.objects_list:
            return False
        if "obtainable" not in object_to_get.properties:
            return False
        if "buy" in object_to_get.properties:
            if self.zorkmids < int(object_to_get.properties[0]):
                self.feedback = f"You need {g.sorf(object_to_get.properties[0])} zorkmids to buy the {object_to_get.name}. Come back when you have some money!"
                return False
        self.get(object_to_get)
        return True

    # Parts of the push function that can't go in the entity class (eg inventory stuff, object properties)
    # Consider making other tryX functions that call the main version. playerPush might be a better name?
    def tryPush(self, direction):
        self.facing = direction
        if e.isEntityAt(self.getCoordsInDir(direction)[0], self.getCoordsInDir(direction)[1], e.entities_list_without_walls):
            entity_to_push = e.getEntityAt(self.getCoordsInDir(direction)[0], self.getCoordsInDir(direction)[1], e.entities_list_without_walls)
            if entity_to_push in e.objects_list_without_walls:
                # Object properties stuff in this block
                if "property" in entity_to_push.properties:
                    pass
            if self.push(direction):
                return True
        return False

    # Main movement function. Calls tryPush, move, get
    def walk(self, direction, distance=1):
        self.facing = direction
        for step in range(distance):
            if not self.tryPush(direction):
                # if push fails, try to pick up the thing
                self.attemptGet()
            self.move(self.getCoordsInDir(direction)[0], self.getCoordsInDir(direction)[1])

    # calls push
    # slot is -1 by default, but can be called at 0 for "throw on use"
    def throw(self, slot_to_throw):
        # 1: check in front of you for closest unblocked space
        # 2: check if there's a player, give it to them if possible
        # 3: else find the nearest unblocked space, move there
        if len(self.inventory) <= 0:
            return False

        item_to_throw = self.inventory[slot_to_throw]
        object_to_throw = item_to_throw.object_stored
        # If something right in front of you, push it away to make room
        self.push(self.facing)
        # Figure out where to go
        max_throw_range = 4
        throw_x = self.getCoordsInDir(self.facing, max_throw_range)[0]
        throw_y = self.getCoordsInDir(self.facing, max_throw_range)[1]
        # Checks tiles in front of player from furthest to closest. If wall, sets tile before wall as throw location
        # ==> will select the last tile before the first wall
        for throw_dist in range(max_throw_range, 0, -1):
            if e.isEntityAt(self.getCoordsInDir(self.facing, throw_dist)[0], self.getCoordsInDir(self.facing, throw_dist)[1]):
                throw_x = self.getCoordsInDir(self.facing, throw_dist - 1)[0]
                throw_y = self.getCoordsInDir(self.facing, throw_dist - 1)[1]
        # If program can't find anywhere to throw, just get the nearest open tile
        # Probably exploitable to send stuff through walls
        if throw_x == self.x and throw_y == self.y:
            throw_coords = e.getNearestOpenTile(self.x, self.y)
            throw_x = throw_coords[0]
            throw_y = throw_coords[1]
        # At this point there is definitely a throw location
        item_to_throw.owner = object_to_throw
        if "null" not in object_to_throw.properties:
            object_to_throw.sound(f"{object_to_throw.name} disappears in a green flash!")
        object_to_throw.x = throw_x
        object_to_throw.y = throw_y
        self.inventory.remove(item_to_throw)
        self.objDropProperties(object_to_throw)
        # Throw has happened. Now do the object properties
        creatures_nearby = object_to_throw.getEntitiesInRange(1, creatures_list)
        coords_in_front_of_hit = object_to_throw.getCoordsInDir(self.facing)
        entity_hit = e.getEntityAt(coords_in_front_of_hit[0], coords_in_front_of_hit[1])
        if "messy throw" in object_to_throw.properties or "break on throw" in object_to_throw.properties:
            self.feedback += " Bits and pieces of it go flying everywhere!"
            if "messy throw" in object_to_throw.properties:
                object_to_throw.sound(f"The {object_to_throw.name} splats everywhere!")
            else:
                object_to_throw.sound(f"The {object_to_throw.name} scatters everywhere!")
            object_to_throw_coords = e.getNearestOpenTile(413, 612, "prime spiral")
            object_to_throw.x = object_to_throw_coords[0]
            object_to_throw.y = object_to_throw_coords[1]
            object_to_throw.sound(f"{object_to_throw.name} appears in a green flash!")
        # Effects that only affect the entity hit
        if entity_hit in creatures_nearby:
            if "indignity on hit" in object_to_throw.properties and "messy throw" not in object_to_throw.properties:
                if entity_hit in players_list:
                    entity_hit.feedback = f"Being hit by the {object_to_throw.name} indignifies you!"
                entity_hit.indignity += 1
        # Effects that affect everyone next to the object
        for creature in creatures_nearby:
            if "indignity on hit" in object_to_throw.properties and "messy throw" in object_to_throw.properties:
                if creature in players_list:
                    creature.feedback = f"The {object_to_throw.name}splosion indignifies you!"
                    creature.climbRank(4)
                creature.indignity += 1
        return True

    # calls throw, push
    # Pushes objects in the way, without moving yourself
    def drop(self, drop_x=None, drop_y=None):
        drop_x = self.getCoordsInDir(self.facing)[0] if drop_x is None else drop_x
        drop_y = self.getCoordsInDir(self.facing)[1] if drop_y is None else drop_y
        if len(self.inventory) == 0:
            self.push(self.facing)
            return False
        item_to_drop = self.inventory[0]
        object_to_drop = item_to_drop.object_stored
        self.feedback = f"You drop the {object_to_drop.name}."
        drop_onto_creature = False
        if e.isEntityAt(drop_x, drop_y):
            if e.getEntityAt(drop_x, drop_y) in creatures_list:
                drop_onto_creature = True
                drop_recipient = e.getEntityAt(drop_x, drop_y)
                # If saleable (can't sell to players)
                if "sell" in object_to_drop.properties and drop_recipient not in players_list:
                    sell_value = int(object_to_drop.properties[0])
                    if sell_value > drop_recipient.zorkmids:
                        return False
                    else:
                        self.zorkmids += sell_value
                        drop_recipient.zorkmids -= sell_value
                        object_to_drop.properties.remove("sell")
                # Give them the item (what if it has weird drop properties?)
                self.inventory.remove(item_to_drop)
                item_to_drop.owner = drop_recipient
                drop_recipient.inventory.insert(0, item_to_drop)
                drop_recipient.objGetProperties(object_to_drop)
                if len(drop_recipient.inventory) > 3:
                    drop_recipient.feedback = f"Your sylladex is overloaded! It spits out the {drop_recipient.inventory[-1].object_stored.name}."
                    drop_recipient.throw(-1)
            else:
                # Push, and if there's still something in the way give up
                self.push(self.facing)
                if e.isEntityAt(drop_x, drop_y):
                    return False
        if not drop_onto_creature:
            item_to_drop.owner = object_to_drop
            if "null" not in object_to_drop.properties:
                object_to_drop.sound(f"{object_to_drop.name} disappears in a green flash!")
            object_to_drop.x = drop_x
            object_to_drop.y = drop_y
            self.inventory.remove(item_to_drop)
        # Object stuff
        self.objDropProperties(object_to_drop)
        return True

    def eat(self, object_to_eat):
        if "edible X3" in object_to_eat.properties:
            object_to_eat.properties.remove("edible X3")
            object_to_eat.properties.append("edible X2")
        elif "edible X2" in object_to_eat.properties:
            object_to_eat.properties.remove("edible X2")
            object_to_eat.properties.append("edible")
        elif object_to_eat.item in self.inventory and "null" not in object_to_eat.properties:
            self.inventory.remove(object_to_eat.item)
            eat_tp_coords = e.getNearestOpenTile(413, 612, "prime spiral")
            object_to_eat.x = eat_tp_coords[0]
            object_to_eat.y = eat_tp_coords[1]
            object_to_eat.sound(f"{object_to_eat.name} appears in a flash of green light!")
        self.objDropProperties(object_to_eat)
        eat_verb = "scoffs" if self.froglyness < 6 else "KERCHOMS"
        self.sound(f"{self.name} {eat_verb} the {object_to_eat.name}.")
        self.feedback = f"You eat the {object_to_eat.name}."
        if "very frogly" in object_to_eat.properties or "very frogly food" in object_to_eat.properties:
            self.froglyness += 2
            self.feedback += f" FROGLYNESS reached level {self.froglyness}!"
        elif "frogly" in object_to_eat.properties or "frogly food" in object_to_eat.properties:
            self.froglyness += 1
            self.feedback += f" FROGLYNESS reached level {self.froglyness}!"
        if "indignified" in object_to_eat.properties or "indignified food" in object_to_eat.properties:
            self.indignity += 1
        if "very indignified" in object_to_eat.properties or "very indignified food" in object_to_eat.properties:
            self.indignity += 1
        if "extremely indignified" in object_to_eat.properties or "extremely indignified food" in object_to_eat.properties:
            self.indignity += 1
        if "dignified" in object_to_eat.properties or "dignified food" in object_to_eat.properties:
            self.indignity -= 1

    def interact(self):
        entity_to_interact = e.getEntityAt(self.getCoordsInDir(self.facing)[0], self.getCoordsInDir(self.facing)[1])
        if entity_to_interact in e.objects_list:
            if entity_to_interact in e.objects_list_without_walls:
                # OBJECT
                if "vomit bag on interact" in entity_to_interact.properties:
                    if self.indignity < 1:
                        self.feedback = "You aren't indignified enough to throw up."
                    elif "vomit bag full" in entity_to_interact.properties:
                        self.feedback = f"You want to throw up in the {entity_to_interact.name}, but someone has beaten you to it!"
                    else:
                        self.sound(f"{self.name} vomits in the {entity_to_interact.name}!!")
                        self.indignity -= 1
                        entity_to_interact.description += f" The {entity_to_interact.name} is full of vomit."
                        entity_to_interact.properties.append("vomit bag full")
                if "text on interact" in entity_to_interact.properties:
                    self.feedback = entity_to_interact.interact_message
                if "sound on interact" in entity_to_interact.properties:
                    self.sound(f"{self.name} " + entity_to_interact.interact_message)
                if "push on interact" in entity_to_interact.properties:
                    self.push(self.facing)
                if "zorkmids on interact" in entity_to_interact.properties:
                    zorkmids_amount = int(entity_to_interact.properties[0])
                    self.zorkmids += zorkmids_amount
                    self.feedback = f"You found {g.sorf(zorkmids_amount)} zorkmids in the {entity_to_interact.name}."
                    entity_to_interact.properties.remove("zorkmids on interact")
            else:
                # WALL
                pass
        elif entity_to_interact in creatures_list:
            if entity_to_interact == mr_frog:
                # maybe this should be its own function, like NPCs have a interact(self, player): function
                if self.froglyness < 1:
                    self.feedback = "You need LEVEL 1 FROGLYNESS to talk to frogs!"
                elif self.froglyness < 7:
                    mr_frog.sound("MR FROG: ...", 1)
                    if self.zorkmids >= 22:
                        self.zorkmids -= 22
                        self.froglyness += 1
                        self.feedback = f"Mr Frog gives you a ribbing lesson. Now you have LEVEL {self.froglyness} FROGLYNESS."
                    else:
                        self.feedback = "You don't have enough zorkmids to pay for Mr Frog's ribbing lesson."
                else:
                    self.feedback = "Mr Frog refuses to teach you any more. That much froglyness would be dangerous."
            elif isinstance(self, Player):
                self.examine(self.facing)
        else:
            # ROOM (there will always be a room, even if it's ultima)
            room_to_interact = self.getRoom()
            if room_to_interact == r.frogg_furnishings:
                if self.froglyness < 2:
                    self.feedback = "You need LEVEL 2 FROGLYNESS to hop!"
                else:
                    self.sound(f"{self.name} hops up and down.")
            elif room_to_interact == r.null_room:
                self.feedback = "Your meditate on nothingness, and bring into being a cube of green foam."
                self.sound(f"{self.name} meditates on nothingness, and brings into being a cube of green foam.")
                self.inventory.insert(0, e.pgenobj.item)

    # Doesn't care what room you're in (specific items might do though)
    def use(self):
        if len(self.inventory) == 0:
            if self.froglyness < 5:
                self.feedback = "You need LEVEL 5 FROGLYNESS to croak!"
            else:
                self.sound(f"{self.name} croaks loudly.", 2 * self.froglyness - 4)
                # This croak could have niche applications relying on being usable above 6 froglyness
                # It basically means if you have 7 unmodified froglyness you can both ribbit and croak
            return False
        coords_use_on = self.getCoordsInDir(self.facing)
        use_on_type = []
        if e.isEntityAt(coords_use_on[0], coords_use_on[1]):
            use_on_type.append("ENTITY")
            entity_use_on = e.getEntityAt(coords_use_on[0], coords_use_on[1])
            if entity_use_on in e.objects_list:
                use_on_type.append("OBJECT")
            elif entity_use_on in creatures_list:
                use_on_type.append("CREATURE")
                if entity_use_on in players_list:
                    use_on_type.append("PLAYER")
                if entity_use_on in npcs_list:
                    use_on_type.append("NPC")
        object_to_use = self.inventory[0].object_stored
        if "edible" in object_to_use.properties or "edible X2" in object_to_use.properties or "edible X3" in object_to_use.properties:
            self.eat(object_to_use)
        if "text on use" in object_to_use.properties:
            self.feedback = object_to_use.use_message
        if "sound on use" in object_to_use.properties:
            self.sound(f"{self.name} " + object_to_use.use_message)
        if "throw on use" in object_to_use.properties:
            self.feedback = f"You throw the {object_to_use.name}."
            self.throw(0)
            entity_in_front_of_throw = e.getEntityAt(object_to_use.getCoordsInDir(self.facing)[0], object_to_use.getCoordsInDir(self.facing)[1])
            if entity_in_front_of_throw in creatures_list:
                entity_in_front_of_throw.feedback = f"The {object_to_use.name} catapults into your sylladex!"
                entity_in_front_of_throw.get(object_to_use)
        if "throw last item on use" in object_to_use.properties:
            if "pulled back" in object_to_use.properties:
                self.feedback = f"You throw the {self.inventory[-1].object_stored.name}."
                self.throw(-1)
            else:
                self.feedback = f"You pull back the {object_to_use.name}, ready to use it."
                object_to_use.properties.append("pulled back")
        if "rank on use" in object_to_use.properties:
            if isinstance(self, Player):
                rank_to_get = int(object_to_use.properties[0])
                if self.rank == rank_to_get:
                    self.feedback = f"You have already reached RANK {rank_titles[self.rank]}."
                elif rank_to_get in self.ranks_achieved and "can repeat rank" not in object_to_use.properties:
                    pass
                else:
                    self.climbRank(rank_to_get)
        # what if vomit bags automatically save you when you're on max indignity?
        if "vomit bag on use" in object_to_use.properties and "vomit bag full" not in object_to_use.properties:
            if self.indignity < 1:
                self.feedback = "You aren't indignified enough to throw up in that. Not yet."
            elif "vomit bag full" in object_to_use.properties:
                self.feedback = f"You try to throw up in the {object_to_use.name}, but someone has beaten you to it!"
            else:
                self.sound(f"{self.name} vomits in the {object_to_use.name}!!")
                self.indignity -= 1
                object_to_use.description += f" The {object_to_use.name} is full of vomit."
                object_to_use.properties.append("vomit bag full")
        return True

    def indignityTithe(self):
        self_is_player = isinstance(self, Player)
        if self.indignity >= min(self.indignity_threshold, 10):
            tithe_amount = min(22 * (self.indignity - (self.indignity_threshold - 2)), self.zorkmids)
            tithe_recipients = []
            for elm in creatures_list:
                if elm == self:
                    pass
                elif elm.indignity >= min(elm.indignity_threshold, 10):
                    pass
                elif abs(elm.x - self.x) + abs(elm.y - self.y) != 1:
                    pass
                else:
                    tithe_recipients.append(elm)
            if len(tithe_recipients) > 0:
                tithe_per_person = tithe_amount // len(tithe_recipients)
                tithe_remainder = tithe_amount - (tithe_amount // len(tithe_recipients) * len(tithe_recipients))
                self.zorkmids -= tithe_amount
                self.indignity -= tithe_amount // 22
                # Pay the tithe
                for tithe_recipient in tithe_recipients:
                    tithe_recipient.zorkmids += tithe_per_person
                random.choice(tithe_recipients).zorkmids += tithe_remainder
                if tithe_amount > 0:
                    self.sound(f"{self.name} pays an Indignity Tithe of {g.sorf(tithe_amount)} zorkmids.")
            if self.indignity < self.indignity_threshold:
                if self_is_player:
                    self.feedback = "You are no longer indignified. Phew!"
            else:
                # Indignity consequences
                if self_is_player:
                    self.feedback = "You are too indignified to continue shopping!!"
                if g.turn_count % 6 == 0:
                    self.sound(f"{self.name} is indignified!! They dribble incoherently on the floor.")
                if g.turn_count % 6 == 2:
                    if self.indignity >= 10:
                        for creature_nearby in self.getEntitiesInRange(1, creatures_list):
                            if creature_nearby != self:
                                creature_nearby.indignity += 1
                                creature_nearby.sound(
                                    f"{self.name} vomits everywhere! You feel indignified just being near them.", 0)
                if g.turn_count % 6 == 4:
                    indig_inv_item_found = False
                    for inv_item in self.inventory:
                        if not indig_inv_item_found:
                            inv_obj = inv_item.object_stored
                            if "indignified" in inv_obj.properties or "very indignified" in inv_obj.properties or "extremely indignified" in inv_obj.properties:
                                self.sound(f"{self.name} clutches the {inv_obj.name} to their chest like an idol!", 2)
                                indig_inv_item_found = True
            return True
        return False


class Player(Creature):
    def __init__(self, name, x, y, description, image):
        # From Entity
        self.x = x
        self.y = y
        self.description = description
        self.name = name
        self.image = image
        e.entities_list.append(self)
        e.entities_list_without_walls.append(self)
        # From Creature
        self.facing = 0
        self.inventory = []
        self.zorkmids = 121
        self.indignity = 0
        self.indignity_threshold = 3
        self.froglyness = 2 if "frog" in self.name.lower() else 0
        self.turns_until_frog_tp = 10
        self.feedback = ""
        self.recent_events = ["WELCOME TO FROGG FURNISHINGS", "A WORLD OF ADENTURE AWITS", "HAVE A HOPPY DAY", "ALL CROAKS RESERVED", ""]
        creatures_list.append(self)
        # Player-specific
        self.command_input = ""
        self.movement_in_command = False
        self.command = ""
        self.game_controls = {}
        self.movement_controls = []
        self.map = []
        self.rank = 1
        self.ranks_achieved = [1]
        self.is_current_turn = False

    def examine(self, direction):
        thing_to_x = e.getEntityAt(self.getCoordsInDir(direction)[0], self.getCoordsInDir(direction)[1])
        if thing_to_x == e.null_entity:
            if len(self.inventory) != 0:
                thing_to_x = self.inventory[0].object_stored
            else:
                thing_to_x = self.getRoom()
        self.feedback = thing_to_x.name.upper() + ": " + thing_to_x.description

    # this command is really messy, mostly because I don't know how NPCs work yet
    def speak(self):
        # NPC reactions are handled by the NPC? But if they have a UI it can't be on the NPC's turn.
        # Figure out if you're talking to someone
        coords_speaking_to = self.getCoordsInDir(self.facing)
        entity_speaking_to = e.getEntityAt(coords_speaking_to[0], coords_speaking_to[1])
        if entity_speaking_to in frogs_list:
            action_taken = "talk to frogs"
        elif entity_speaking_to in creatures_list:
            action_taken = "talk to anyone"
        else:
            action_taken = "speak"

        # Error feedback
        low_froglyness = (self.froglyness <= ribtionary.get(action_taken))
        if low_froglyness:
            self.feedback = f"You need LEVEL {ribtionary.get(action_taken)} FROGLYNESS to {action_taken}!"
        elif self.froglyness >= 10:
            self.feedback = "Your Froglyness is too high! Reduce your froglyness!!"

        # if you are speaking *to* someone, message ought to be different
        # If speaking: rib message
        if self.froglyness <= 0:
            if self.indignity < 4:
                self.sound(f"{self.name} tries to croak, but nothing comes out.", 1)
            else:
                self.sound(f"Unable to speak in froglish, {self.name} declares something horrible in French.", 5)
        elif self.froglyness == 1:
            # you can talk to frogs
            ribbit_verb = "gurgle" if self.indignity < 4 else "burp"
            self.sound(f"{self.name} {ribbit_verb}s in broken froglish.", 1)
        elif self.froglyness < 4:
            ribbit_adj = "modestly" if self.froglyness == 2 else "happily"
            self.sound(f"{self.name} ribs {ribbit_adj}.", self.froglyness)  # 3 frogly ... 2*4 - 3 = 5, 2*5 - 4 = 6
        elif self.froglyness < 7:
            self.sound(f"{self.name} croaks loudly.", 2 * self.froglyness - 4)  # range inc by 2/lvl
        elif self.froglyness < 9:
            self.sound(f"{self.name} ribbits magnificently!", 2 * self.froglyness - 4)
        elif self.froglyness == 9:
            self.sound(f"{self.name} ribbits with dangerous vigour!", 2 * self.froglyness - 4)
        elif self.froglyness >= 10:
            self.sound(f"{self.name}'s throat expands to the size of a car. They riblease an explosive cry for help!!", 2 * self.froglyness - 4)  # range 16 at 10 frogly
            # this line is too long to fit on the screen with the default screen size

    def startTurn(self):
        if self.getRoom() == r.null_room:
            if self.froglyness <= 0:
                frog_tp_coords = e.getNearestOpenTile(0, 0)
                self.x = frog_tp_coords[0]
                self.y = frog_tp_coords[1]
            if g.turn_count % 20 == 0:
                self.turns_until_frog_tp = 25
                self.froglyness -= 1
                self.zorkmids += 22
        self.command_input = ""
        self.command = ""
        self.movement_in_command = False
        self.indignity = max(min(self.indignity, 10), 0)
        self.froglyness = max(min(self.froglyness, 10), 0)
        self.is_current_turn = True
        # Indignity Tithe (if you're indignified, automatically lower it by donating zorkmids or throwing indig objects)
        if self.froglyness >= 10:
            self.feedback = "You can't contain this much froglyness!! Reduce your froglyness!"
            self.turns_until_frog_tp -= 1
            if g.turn_count % 4 == 0:
                self.sound(f"{self.name} glows with froglyness", 12 - self.turns_until_frog_tp)
            if self.turns_until_frog_tp == 0:
                for creature in self.getEntitiesInRange(1, e.entities_list_without_walls):
                    frog_tp_coords = e.getNearestOpenTile(413, 612, "prime spiral")
                    creature.sound(f"{self.name} disappears in an explosion of frogly green light!!")
                    creature.x = frog_tp_coords[0]
                    creature.y = frog_tp_coords[1]
                    creature.feedback = "The froglyness consumes you, and spits you out into the ether of another world!"
                    creature.turns_until_frog_tp = 50
                if 4 not in self.ranks_achieved:
                    self.climbRank(5)
                return False
        elif self.turns_until_frog_tp < 10:
            self.turns_until_frog_tp += 1
        if self.indignityTithe():
            if 0 not in self.ranks_achieved:
                self.climbRank(0)
            return False
        if self.zorkmids < 0:
            self.feedback = f"You are in zorkdebt!! How indignified!"
            self.indignity += 1
        if abs(self.x - e.radio.item.owner.x) <= 1 and abs(self.y - e.radio.item.owner.y) <= 1:
            if (g.turn_count // 2) % len(e.radio_script) in [3, 4, 5]:
                if 3 not in self.ranks_achieved:
                    self.climbRank(3)
        return True

    # WARNING!!! Whenever you add a new rank to rank_titles, every rank after it will move over
    # And any functions referring to it will be wrong.
    # full rank planning at the top of Furnishings Planning.txt
    def climbRank(self, rank_number):
        if rank_number >= len(rank_titles):
            return False
        if rank_number == self.rank:
            return False
        self.ranks_achieved.append(rank_number)
        rank_verb = "just climbed" if self.rank < rank_number else " was demoted"
        self.rank = rank_number
        self.sound(f"{self.name} {rank_verb} to RANK {rank_titles[rank_number]}", 10)
        return True


# Things in this class are mostly for special talking and merchant interfaces
# Don't know if it needs its own init function yet
# NPCs have their own secret turn
# They go through their recent events and look for anything important, then react to it
# They might also move at the start of it, or writhe on the floor, etc
class Npc(Creature):
    def __init__(self, name, x, y, description, image, zorkmids, indignity, froglyness):
        # From Entity
        self.x = x
        self.y = y
        self.description = description
        self.name = name
        self.image = image
        e.entities_list.append(self)
        e.entities_list_without_walls.append(self)
        # Creature-specific
        self.facing = 0
        self.inventory = []
        self.zorkmids = zorkmids
        self.indignity = indignity
        self.indignity_threshold = 3
        self.froglyness = froglyness
        self.turns_until_frog_tp = 10
        self.feedback = ""
        self.recent_events = [""]
        creatures_list.append(self)
        # NPC-specific
        self.turn_used = False  # maybe this is what the stat should be called for Players, it just works differently
        npcs_list.append(self)
        # a bunch of variables like 'reaction_to_steal', 'reaction_to_talk'. Probably pretty lengthy.


mr_frog = Npc("Mr Frog", -8, 0, "An wise frog with a red fez. He watches the world with froggy yellow eyes.", ["  *  ", " *F* ", "  *  "], 99, 0, 20)
mr_frog.indignity_threshold = 10
mr_swastika = Npc("Mr Swastika", -4, 7, "A diminutive baker with a swastika on his apron. He seems friendly enough.", ["  *  ", " *S* ", "  *  "], 99, 0, 4)
# mr swastika can't become indignified, but has trouble if you dignify him. he will eat things to redignify himself.
# or, appease him by giving him the swastika
mr_kolunu = Npc("Mr Kolunu", 5, 8, "A hunched frog in raggedy robes. Flies buzz around him like vultures, except tiny and annoying.", ["  *  ", " *K* ", "  *  "], 99, 0, 7)
# mr_frog = Npc(name x y desc img zork ind frog)
