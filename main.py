import graphics as g
import entity as e
import player as p
import map as m
import functions as f
from random import choice
from time import sleep
from keyboard import is_pressed

spiral_nulds = []
for i in range(11000):
    print("LOADING " + "<" * (i // 1000) + m.frogly_faces[i // 1000])
    if i % 90 == 0:
        spiral_nulds.append("")
        nuld_coords = e.getNearestOpenTile(413, 612, "prime spiral")
        spiral_nulds[-1] = e.Object("Prime Nuld", nuld_coords[0], nuld_coords[1], [],
                                          "(its description is self-evident and does not need stating.)",
                                          ["+++++", "+   +", "+++++"])
p.mr_kolunu.get(e.kolunu_crackers)
p.mr_swastika.get(e.swastika_badge)
p.mr_swastika.get(e.corpse)

# Main game mechanics:
# inventory management
# pushing things? (objects can technically push people. some objects should do that when you interact with them)
# using items on people (part of Use fn)
# froglyness!! and going to 10 froglyness.
# also ribbiting. Varied NPC responses based on froglyness. different quests etc
# eg low froglyness ==> you get past the guards as they wont touch you
# Indignification as zorkmid theft. NPC theft via indignification (will probably have to move indig fn into Creature)
# add npc indignity

f.initialiseWalls(g.map_walls)
player_descriptions = ["They're the worst.", "They're only in it for the money.",
                       "Their job application got rejected - now they're back for blood.",
                       "They'll be the first against the wall when the revolution comes.",
                       "They'll be the first to raise their bat when the revolution comes.",
                       "They'd rather be in bed.", "Their passing will not be mourned.",
                       "They're hunting for the perfect pasty to bring home.", "No comment."]

# Starting UI
print("Welcome to Frogg Furnishings.")
# Initialise players
frogspawn_points = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [-1, 1], [1, 1], [-1, -1], [1, -1]]
g.player_count = max(min(f.getInput("How many people are playing? (up to 3) ", ["is_number"]), 3), 1)
for player_to_add in range(g.player_count):
    player_name_input = f.getInput(f"Player {player_to_add + 1} name: ")[:20]
    p.players_list.append("")
    player_spawn_coords = e.getNearestOpenTile(frogspawn_points[player_to_add][0], frogspawn_points[player_to_add][1])
    player_spawn_x = player_spawn_coords[0]
    player_spawn_y = player_spawn_coords[1]
    player_description = choice(player_descriptions)
    p.players_list[player_to_add] = p.Player(player_name_input, player_spawn_x, player_spawn_y,
                                             f"This is {player_name_input}. " + player_description,
                                             ["     ", "  @  ", "     "])

p.players_list[0].movement_controls = ["W", "D", "S", "A"]
p.players_list[0].game_controls = {
    "W": "NORTH",
    "A": "WEST",
    "S": "SOUTH",
    "D": "EAST",
    "Q": "INTERACT",
    "E": "USE",
    "F": "GET",
    "C": "DROP",
    "Z": "SPEAK",
    "X": "EXAMINE",
    "/": "END"
}
if len(p.players_list) >= 2:
    p.players_list[1].movement_controls = ["I", "L", "K", "J"]
    p.players_list[1].game_controls = {
        "I": "NORTH",
        "J": "WEST",
        "K": "SOUTH",
        "L": "EAST",
        "U": "INTERACT",
        "O": "USE",
        ";": "GET",
        ":": "GET",
        ".": "DROP",
        ">": "DROP",
        "M": "SPEAK",
        ",": "EXAMINE",
        "<": "EXAMINE",
        "/": "END"
    }
if len(p.players_list) >= 3:
    p.players_list[2].movement_controls = ["8", "6", "5", "4"]
    p.players_list[2].game_controls = {
        "8": "NORTH",
        "4": "WEST",
        "5": "SOUTH",
        "6": "EAST",
        "7": "INTERACT",
        "9": "USE",
        "3": "GET",
        "0": "DROP",
        "1": "SPEAK",
        "2": "EXAMINE",
        "/": "END"
    }

input("""
Make sure the screen is big or it'll look like garbage.
Press '/' to end the game and view the scoreboard.
Press a movement key and an action key at the same time to turn without moving.
Get the most froglyness and the least indignity!
PRESS ENTER TO BEGIN: """)

# Main loop
# turn count is stored in graphics module, to make it easier to call
while g.game_afoot:
    # Start of round
    # Anything that objects do automatically happens
    e.objectActions()
    # start turn for every player (startTurn probably shouldn't be a player function anymore)
    for player in p.players_list:
        player.startTurn()
    # print map
    m.printMap()
    # Get user input
    sleep(0.2)
    for input_tick in range(11):
        sleep(0.05)
        for player in p.players_list:
            for key in player.game_controls:
                if is_pressed(key):
                    if key in player.movement_controls and key not in player.command_input:
                        if not player.movement_in_command:
                            player.command_input += key
                            # Change player facing to whichever movement key is pressed
                            for direction in range(4):
                                if key == player.movement_controls[direction]:
                                    player.facing = direction
                        player.movement_in_command = True
                    else:
                        player.command_input += key
        if is_pressed("/"):
            g.game_afoot = False
    # Interpret user input
    for player in p.players_list:
        f.sanitiseCommandInput(player)
        if len(player.command_input) == 0:
            player.command = "PASS"
        elif len(player.command_input) == 1:
            player.command = player.game_controls.get(player.command_input)
        else:   # ie is command.len >= 2
            # this part doesn't work
            command_found = False
            for letter in player.command_input:
                if letter not in player.movement_controls and not command_found:
                    player.command = player.game_controls.get(letter)
                    command_found = True
    # vestigial code from v0.3
    # game_input = f.getInput("INPUT ACTION: ", []).upper()
    # f.interpretInput(game_input)
    for player in p.players_list:
        if g.game_afoot and player.indignity < player.indignity_threshold:
            # Execute player inputs
            # Interpret input - if not in controls, do the interaction for when there isn't an object
            if player.command == "NORTH":
                player.walk(0)
            elif player.command == "EAST":
                player.walk(1)
            elif player.command == "SOUTH":
                player.walk(2)
            elif player.command == "WEST":
                player.walk(3)
            elif player.command == "INTERACT":
                player.interact()
            elif player.command == "USE":
                player.use()
            elif player.command == "GET":
                player.attemptGet()
            elif player.command == "DROP":
                player.drop()
            elif player.command == "EXAMINE":
                player.examine(player.facing)
            elif player.command == "SPEAK":
                player.speak()
            elif player.command == "END":
                g.game_afoot = False
            else:
                pass
            # End of turn (if time proceeds automatically, remove map redraw)
        if f.checkForGameEnd():
            g.game_afoot = False
        if g.player_count > 1 and g.game_afoot:
            player.is_current_turn = False
    # Possible NPC turn?
    f.npcTurn()
    # Check any other win conditions
    g.turn_count += 1
f.scoreboard()
sleep(60)
