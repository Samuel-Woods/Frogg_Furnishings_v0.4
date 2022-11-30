# Initialising variables that need to be accessible from anywhere
# GLOBAL STUFF
turn_count = 0
player_count = 3
game_afoot = True
sorf_digits = ["0", "1", "2", "§", "3", "4", "5", "6", "7", "8", "9"]


# Converts a number into sorf maths
def sorf(num_unsorfed):
    num_unsorfed = int(num_unsorfed)
    if num_unsorfed == 0:
        return "0"
    num_sorfed = ""
    while num_unsorfed > 0:
        digit = num_unsorfed % 11
        num_sorfed = sorf_digits[digit] + num_sorfed
        num_unsorfed = (num_unsorfed - digit) // 11
    return num_sorfed


# OPENING TIME IS 400 ≡ 4:13 AM         (552≡6:12, 875≡10:25)
def sorfTime():
    start_time = 400    # 4:13 AM
    current_time = start_time + turn_count
    sorf_minutes = sorf(current_time % 77)  # 77 ==> 60 minutes in an hour  27 ==> 24 hours in a day
    # 12 hours in AM, 1§ hours in PM
    sorf_am = "AM" if (current_time // 77) % 27 < 13 else "PM"
    sorf_hours = sorf((current_time // 77) % 27) if sorf_am == "AM" else sorf((current_time // 77) % 27 - 13)
    sorf_minutes = "0" * (2 - len(sorf_minutes)) + sorf_minutes
    if sorf_hours == "0" and sorf_am == "PM":
        sorf_hours = "12"
    return f"{sorf_hours}:{sorf_minutes} {sorf_am}"


# Sentence to remove must be missing full stop to work, e.g. removeSentence("One. Two. Three.", "Two")
def removeSentence(text, sentence_to_remove):
    text_as_array = text.split(". ")
    if sentence_to_remove in text_as_array:
        text_as_array.remove(sentence_to_remove)
    if sentence_to_remove + "." in text_as_array:
        text_as_array.remove(sentence_to_remove + ".")
    text_result = ""
    for sentence in range(len(text_as_array)):
        text_result += text_as_array[sentence]
        if text_result[-1] != ".":
            text_result += "."
        if sentence < len(text_as_array) - 1 and len(text_as_array):
            text_result += " "
    return text_result

# room floor tiles: ∙-=≈≡#░▒▓
# wall chars: O═║╔╗╚╝╠╣╩╦╬
# wall chars:  ─│┌┐└┘├┤┴┬┼
# wall chars: ╢╞╧╤ for joining the two types
# creature chars: use letters. children and animals get lowercase letters? or just animals
# ≈ water       use capital Pi for tables.
# ΘτΓΦΩ furniture, ☼gem ►
# ♣♠ plants ♥ ¶ grilk bottle? α fish
# ♂ bag (zorkmid bag!) ♀ amulet
# *+=o x|£√¥ ↕ ↔ ^
# Next to none of the following actually render
# ■□▢▣ ▤▥▦▧▨▩ ▪▫▬▭▮▯▰▱ ▲△▴▵▶▷▸▹►▻▼▽▾▿◀◁◂◃◄◅◆◇◈◉◊○◌◍◎● ◐◑◒◓◔◕
# ◖◗ ◙◚◛ ◜◝◞◟◠◡ ◦
# ◢◣◤◥ ◧◨◩◪◫ ◬ ◭◮ ◯ ◰◱◲◳◴◵◶◷ ◿◺◹◸◻◼◽◾ ▲△/▶▷/▼▽/◀◁


blank_image = ["     ", "     ", "     "]
# player0 = default, player1 = current turn player, player2 = indignified
# def playerUpdateImage that gets called at the start of every printMap
player_graphics_default = [["  ^  ", "  @  ", "     "], ["     ", "  @> ", "     "], ["     ", "  @  ", "  v  "], ["     ", " <@  ", "     "]]
player_graphics_current_turn = [["  ▲  ", "  @  ", "     "], ["     ", "  @► ", "     "], ["     ", "  @  ", "  ▼  "], ["     ", " ◄@  ", "     "]]
player_image_indignified = ["     ", " !@! ", "     "]
wall_graphics = [["░░░░░", "░░░░░", "░░░░░"], ["▒▒▒▒▒", "▒▒▒▒▒", "▒▒▒▒▒"], ["▓▓▓▓▓", "▓▓▓▓▓", "▓▓▓▓▓"], ["#####", "#####", "#####"]]
door_graphics = [["     ", "░====", "     "], ["     ", "====░", "     "]]
water_graphics = [["≈≈≈≈≈", "≈≈≈≈≈", "≈≈≈≈≈"], [" ≈≈≈≈", "≈≈≈≈≈", "≈≈≈≈≈"], ["≈≈≈≈ ", "≈≈≈≈≈", "≈≈≈≈≈"],
                  ["≈≈≈≈≈", "≈≈≈≈≈", "≈≈≈≈ "], ["≈≈≈≈≈", "≈≈≈≈≈", " ≈≈≈≈"]]


# WORLD MAP
# This world map is in 1x1 graphics instead of 5x3, to tell the initialiseWalls function where to put walls
# +X/+Y : >/^    top corner currently offset by 10, 5 from the bottom left corner
# 21px wide, 16px high
map_walls = ["      #######          ",
             "    ###     #####      ",
             "    #       #   #      ",
             "    #           ####   ",
             "    #  #  ###      ##  ",
             "    ####    ## ###  #  ",
             "#####       #   ##  #  ",
             "#   #              ##  ",
             "#           #    # #   ",
             "## ############ ## ####",
             " #      #   #    #    #",
             " #        @      ##   #",
             " #≈≈    #   #         #",
             " #≈≈≈≈≈### ######     #",
             " #≈≈≈≈≈#        #######",
             " ################      "]
# main boundaries: [-2, -6] to [6,10]

# WORLD MAP ZOOMED OUT (F - frogg furnishings)
# Every px in the paint document is 5x5 in-world, so the map is 350x250
# If that feels too cramped, change it to 10x10 (700x500)
world_map_zoomed_out = ["                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        "                                   ",
                        ]
# take this image and convert it
# # = natural walls
# ░ walls in darkness
# ▒ normal walls
# ▓ very bright walls, chalky cliffs??
# ≈ = water
# biomes!!
# “” special quotation marks
# ["%   %", " % % ", "  %  "] pretty room graphics for a flower field
