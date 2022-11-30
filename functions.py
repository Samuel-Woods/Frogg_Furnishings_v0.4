import graphics as g
import entity as e
import player as p
import map as m
import random

import room

# THE RULES OF THE RIB:
# 0:        mr swastika will give you a sale (he also takes money off for every point of indignity you have)
# 1: toad   can eat bugs, can talk to frogs (maybe mr frog takes payment in the form of frogly items?)
#           permanently converting the item to froglyness, but froglyness is easier to lose (eg by overloading)
#           and he'll refuse to teach you beyond lv7
#           should mr frog really be the villain? idk. how else to add stakes?
#           maybe you overload on froglyness lower earlier in the game?? at like 3, and it increases gradually
# 2: lilypad can sit on lilypads, can rib
# 3: hop    can hop
#    rib    can rib
# 4: frog hop (the dance), can eat bigger bugs
# 5: croak      can croak
# 6: kerchom    can eat really big bugs
# 7: ribbit     you have a lovely ribbit
# if using the lilypad is something powerful, it should have a higher requirement

ribtionary = {
    "ribbit": 7,
    "kerchom": 6,
    "croak": 5,
    "rib": 3,
    "frog": 2,
    "hop": 2,
    "lily pad": 2,
    "lilypad": 2,
    "toad": 1}


def sanitiseCommandInput(player):
    result = ""
    movement_command = ""
    for character in player.command_input:
        if character not in result:
            if character.upper() in player.movement_controls:
                movement_command = character
            else:
                result += character
    player.command_input = result.upper() + movement_command


# ACTION    PRIMARY SECONDARY   NUMPAD?     MOUSE (bad design atm) (Ctrl and Shift work alright on my keyboard)
# MOVE/PUSH WASD    IJKL        8456        Arrows
# INTERACT  Q       U           7           M3/M4?
# USE       E       O           9           M3?
# GET       F       ;:          0? Enter?   M1      Auto-wears items (code in clothes visibility, or don't add it.)
# DROP      C       .>          3           M2
# SPEAK     Z       M           1           (?)
# EXAMINE   X       ,<          2           M5?


def interpretInput(user_input):
    # Get parts of the input that actually correspond to commands
    # if multiple players, get user_input_p1, user_input_p2, user_input_p3
    # Get useful parts of the input
    for player in p.players_list:
        player.command_input = ""   # input_useful
        player.command = ""         # command
        player.movement_found_in_command = False  # movement_found
        for letter in user_input:
            if letter in player.game_controls.keys() and letter not in player.command_input:
                if letter not in player.movement_controls:
                    player.command_input += letter
                elif not player.movement_found_in_command:
                    player.command_input += letter
                    player.movement_found_in_command = True
        if len(player.command_input) == 0:
            player.command = "PASS"
        if len(player.command_input) == 1:
            player.command = player.game_controls.get(player.command_input)
        else:
            # real-time version of this is making facing change instantly, but motion only after holding down briefly
            # facing_found and command_found are to ensure only the first facing & command are used
            facing_found = False
            command_found = False
            for letter in player.command_input:
                if letter in player.movement_controls:
                    if not facing_found:
                        if letter == player.movement_controls[0]:
                            player.facing = 0
                        if letter == player.movement_controls[1]:
                            player.facing = 1
                        if letter == player.movement_controls[2]:
                            player.facing = 2
                        if letter == player.movement_controls[3]:
                            player.facing = 3
                        facing_found = True
                elif not command_found:
                    player.command = player.game_controls.get(letter)
                    command_found = True
    # Doesn't return anything as it changes the values in Player instead
    # Only want one movement command!!
    # if command has only 1 viable input, just use that
    # if there is a movement *and* any other command, you change facing and use the other command


def initialiseWalls(wall_map):
    e.walls_list = []
    x_offset = 10
    y_offset = 5
    for row in range(len(wall_map)):
        e.walls_list.append([])
        for tile in range(len(wall_map[row])):
            e.walls_list[row].append("")
            x_to_place = tile - x_offset
            y_to_place = len(wall_map) - row - y_offset
            if wall_map[row][tile] != " ":
                if e.isEntityAt(tile - x_offset, len(wall_map) - row - y_offset, e.entities_list_without_walls):
                    print(f"Wall collision at {tile}, {len(wall_map) - row}")
                if wall_map[row][tile] == "#":
                    e.walls_list[row][tile] = e.Object("Wall", x_to_place, y_to_place, [],
                                                       "A wall blocks your path! Hope you know how to turn around.", g.wall_graphics[1])
                    e.entities_list_without_walls.remove(e.walls_list[row][tile])
                    e.objects_list_without_walls.remove(e.walls_list[row][tile])
                elif wall_map[row][tile] == "≈":
                    e.walls_list[row][tile] = e.Object("Water", x_to_place, y_to_place, [],
                                                       "This is water.", g.water_graphics[0])
                    e.entities_list_without_walls.remove(e.walls_list[row][tile])
                    e.objects_list_without_walls.remove(e.walls_list[row][tile])


# conditions: not_empty, lower, is_number
def getInput(input_prompt, conditions=None):
    if conditions is None:
        conditions = ["not_empty"]
    user_input = ""
    conditions_met = False
    while not conditions_met:
        user_input = input(input_prompt)
        if "lower" in conditions:
            user_input = user_input.lower()
        if "not_empty" in conditions and user_input == "":
            print("Empty input not allowed.")
            pass
        elif "is_number" in conditions:
            try:
                user_input = int(user_input)
                conditions_met = True
            except ValueError:
                print("Not a number.")
        elif "is_direction" in conditions:
            pass
        elif "is_player" in conditions:
            pass
        elif "is_object" in conditions:
            pass
        else:
            conditions_met = True
    return user_input


def scoreboard():
    # Time message
    minutes = g.sorf(g.turn_count % 77)
    hours = g.sorf((g.turn_count // 77) % 27)
    days = g.sorf(g.turn_count // (77 * 27))
    minutes_plural = "" if minutes == "1" else "S"
    hours_plural = "" if hours == "1" else "S"
    days_plural = "" if days == "1" else "S"
    minutes_message = "" if minutes == "0" else f"{minutes} MINUTE{minutes_plural}"
    hours_message = "" if hours == "0" else f"{hours} HOUR{hours_plural}, "
    days_message = "" if days == "0" else f"{days} DAY{days_plural}, "
    print(f"YOU SHOPPED UNTIL YOU DROPPED AFTER {days_message}{hours_message}{minutes_message}.")
    # Score message
    print("NAME                ZORKMIDS  INDIGNITY   FROGLYNESS      FINAL RANK")
    for rank_number in range(len(p.rank_titles), -1, -1):
        for player in p.players_list:
            if player.rank == rank_number:
                score_name = player.name[0:19] + " " * max(20 - len(player.name[0:19]), 0)
                score_zorkmids = f"{g.sorf(player.zorkmids)}zm"
                score_zorkmids += " " * max(10 - len(score_zorkmids), 0)
                score_indignity = "Ø " * min(player.indignity, 6) + "O " * max(player.indignity_threshold - player.indignity, 0)
                score_indignity += " " * max(12 - len(score_indignity), 0)
                score_froglyness = "<"*min(player.froglyness, 10) + m.frogly_faces[min(player.froglyness, 10)]
                score_froglyness += " " * max(16 - len(score_froglyness), 0)
                score_rank = p.rank_titles[player.rank]
                scoreboard_line = score_name + score_zorkmids + score_indignity + score_froglyness + score_rank
                print(scoreboard_line)


# return True if the game should end
def checkForGameEnd():
    # End game if all players are indignified
    all_players_indignified = True
    for player in p.players_list:
        if player.indignity < min(player.indignity_threshold, 10):
            all_players_indignified = False
    if all_players_indignified:
        print("Everyone is indignified!! Mr Frog kicks you out of the store.")
        return True
    return False


# This would likely be easier to do within the player module
def npcTurn():
    for npc in p.npcs_list:
        npc.turn_used = False
        if npc.indignity >= npc.indignity_threshold:
            npc.turn_used = True
            npc.indignityTithe()
        if npc.getRoom() == room.null_room:
            if g.turn_count % 20 == 0:
                npc.froglyness -= 1
                npc.zorkmids += 22
            if npc.froglyness <= 0:
                frog_tp_coords = e.getNearestOpenTile(0, 0)
                npc.x = frog_tp_coords[0]
                npc.y = frog_tp_coords[1]
    # MR KOLUNU
    if not p.mr_kolunu.turn_used:
        # Move towards colony deed
        if not p.mr_kolunu.turn_used and random.choice([1, 2, 2, 3]) < p.mr_kolunu.distToEntity(e.kolunu_deed) <= 8:
            p.mr_kolunu.walk(p.mr_kolunu.findDirectionTo(e.kolunu_deed.item.owner.x, e.kolunu_deed.item.owner.y))
            p.mr_kolunu.turn_used = True
        if not p.mr_kolunu.turn_used and e.kolunu_deed.item in p.mr_kolunu.inventory:
            p.mr_kolunu.walk(random.choice([0, 1, 2, 3]))
            p.mr_kolunu.turn_used = True
