import graphics as g
import room as r
import entity as e
import player as p

frogly_faces = [":(", ":O", ":)", ":)", ":)", ":D", ":D", ":D", ":D", ":O", ":@", ":@"]
# view dist 4 ==> 4+@+4 = 9x9 map
map_view_dist = 4


def getInvItemName(player, position_in_inv):
    inv_item_name = ""
    if position_in_inv < len(player.inventory):
        inv_item_name = player.inventory[position_in_inv].object_stored.item_name
    return inv_item_name + " " * (max(0, 15 - len(inv_item_name)))


def getInvItemImage(player, position_in_inv):
    inv_item_image = g.blank_image
    if position_in_inv < len(player.inventory):
        inv_item_image = player.inventory[position_in_inv].object_stored.image
    return inv_item_image


def getMap():
    map_width = 10 * map_view_dist + 5
    for player in p.players_list:
        for player_on_map in p.players_list:
            if player_on_map == player:
                player_on_map.image = g.player_graphics_current_turn[player_on_map.facing]
            elif player_on_map.indignity >= min(player_on_map.indignity_threshold, 10):
                player_on_map.image = g.player_image_indignified
            else:
                player_on_map.image = g.player_graphics_default[player_on_map.facing]
        player.map = []
        zorkmids_notif = f" Zorkmids: {g.sorf(player.zorkmids)}zm"
        zorkmids_notif += " " * (map_width - len(zorkmids_notif))
        indignity_notif = " Indignity: "
        indignity_notif += "Ø " * min(player.indignity, 10) + "O " * max(
            player.indignity_threshold - player.indignity, 0)
        indignity_notif += " " * (map_width - len(indignity_notif))
        froglyness_notif = " Froglyness: " + "<" * min(player.froglyness, 11)
        froglyness_notif += frogly_faces[min(player.froglyness, 11)]
        froglyness_notif += " " * (map_width - len(froglyness_notif))
        player.map.append("=" * map_width)
        player.map.append(" " + player.name + " "*max((map_width - len(player.name) - 1), 0))
        player.map.append(zorkmids_notif)
        player.map.append(indignity_notif)
        player.map.append(froglyness_notif)
        player.map.append("=" * map_width)
        for map_y in range(player.y + map_view_dist, player.y - map_view_dist - 1, -1):
            map_row_top = ""
            map_row_mid = ""
            map_row_bot = ""
            for map_x in range(player.x - map_view_dist, player.x + map_view_dist + 1):
                entity_at_coords = e.getEntityAt(map_x, map_y)
                if entity_at_coords == e.null_entity:
                    room_at_coords = r.getRoomAt(map_x, map_y)
                    map_row_top += room_at_coords.image[0]
                    map_row_mid += room_at_coords.image[1]
                    map_row_bot += room_at_coords.image[2]
                else:
                    map_row_top += entity_at_coords.image[0]
                    map_row_mid += entity_at_coords.image[1]
                    map_row_bot += entity_at_coords.image[2]
            player.map.append(map_row_top)
            player.map.append(map_row_mid)
            player.map.append(map_row_bot)
        player.map.append("=" * map_width)
        # INVENTORY
        player.map.append(f"{getInvItemName(player,0)}{getInvItemName(player,1)}{getInvItemName(player,2)}")
        inv_image_0 = getInvItemImage(player, 0)
        inv_image_1 = getInvItemImage(player, 1)
        inv_image_2 = getInvItemImage(player, 2)
        for inv_image_row in range(3):
            player.map.append("  [  " + inv_image_0[inv_image_row] + "  ]       " + inv_image_1[inv_image_row] + " "*10 + inv_image_2[inv_image_row] + " "*5)


def printHUD(max_feed_len):
    print("="*182)
    for player in p.players_list:
        player.feedback += " " * max(2*max_feed_len - len(player.feedback), 0)
        for recent_events_msg in range(-5, 0):
            player.recent_events[recent_events_msg] += " " * max(max_feed_len - len(player.recent_events[recent_events_msg]), 0)
    if g.player_count >= 2:
        print(f" P1 CONTROLS || {p.players_list[0].feedback[:max_feed_len]} ║ {p.players_list[1].feedback[:max_feed_len]} | P2 CONTROLS")
        print(f"WASD|  MOVE  || {p.players_list[0].feedback[max_feed_len:2*max_feed_len]} ║ {p.players_list[1].feedback[max_feed_len:2*max_feed_len]} |UHJK|  MOVE")
        print(" Q  |INTERACT|[" + "="*153 + "] U  |INTERACT")
        print(f" E  |  USE   || {p.players_list[0].recent_events[-5][:max_feed_len]} ║ {p.players_list[1].recent_events[-5][:max_feed_len]} | O  |  USE")
        print(f" F  |  GET   || {p.players_list[0].recent_events[-4][:max_feed_len]} ║ {p.players_list[1].recent_events[-4][:max_feed_len]} | ;: |  GET")
        print(f" C  |  DROP  || {p.players_list[0].recent_events[-3][:max_feed_len]} ║ {p.players_list[1].recent_events[-3][:max_feed_len]} | .> |  DROP")
        print(f" Z  | RIBBIT || {p.players_list[0].recent_events[-2][:max_feed_len]} ║ {p.players_list[1].recent_events[-2][:max_feed_len]} | M  | RIBBIT")
        print(f" X  |EXAMINE || {p.players_list[0].recent_events[-1][:max_feed_len]} ║ {p.players_list[1].recent_events[-1][:max_feed_len]} | ,< |EXAMINE")
    elif g.player_count == 1:
        max_feed_len = 138
        print(f"   CONTROLS  || {p.players_list[0].feedback[:max_feed_len]}")
        print(f"WASD|  MOVE  || {p.players_list[0].feedback[max_feed_len:2 * max_feed_len]}")
        print(" Q  |INTERACT|[" + "=" * 158)
        print(f" E  |  USE   || {p.players_list[0].recent_events[-5][:max_feed_len]}")
        print(f" F  |  GET   || {p.players_list[0].recent_events[-4][:max_feed_len]}")
        print(f" C  |  DROP  || {p.players_list[0].recent_events[-3][:max_feed_len]}")
        print(f" Z  | RIBBIT || {p.players_list[0].recent_events[-2][:max_feed_len]}")
        print(f" X  |EXAMINE || {p.players_list[0].recent_events[-1][:max_feed_len]}")



def printMap():
    print("""
    
    
    
    
    """)
    print("=" * 182)
    getMap()
    map_width = 10 * map_view_dist + 5
    map_indent = 60
    max_feed_len = 86
    if g.player_count >= 2:
        map_indent = 45
        max_feed_len = map_indent - 16 + map_width
    # Printing HUD - different formatting for 2P vs 3P
    if g.player_count <= 2:
        for map_row_count in range(len(p.players_list[0].map)):
            map_row = " " * map_indent + "║"
            for player in p.players_list:
                map_row += player.map[map_row_count] +"║"
            print(map_row)
        printHUD(max_feed_len)
    else:
        map_indent = 10
        p3_controls = ["", "", "", "", "", "=================================", "", "P3 CONTROLS", "8456|  MOVE",
                       " 7  |INTERACT", " 9  |  USE", " 3  |  GET", " 0  |  DROP", " 1  | RIBBIT", " 2  |EXAMINE",
                       "", "=================================", "",
                       p.players_list[2].feedback[:50], p.players_list[2].feedback[50:100],
                       p.players_list[2].feedback[100:150], "", "=================================", "",
                       p.players_list[2].recent_events[-5][:50], p.players_list[2].recent_events[-5][50:100],
                       p.players_list[2].recent_events[-4][:50], p.players_list[2].recent_events[-4][50:100],
                       p.players_list[2].recent_events[-3][:50], p.players_list[2].recent_events[-3][50:100],
                       p.players_list[2].recent_events[-2][:50], p.players_list[2].recent_events[-2][50:100],
                       p.players_list[2].recent_events[-1][:50], p.players_list[2].recent_events[-1][50:100]]
        for map_row_count in range(len(p.players_list[0].map)):
            map_row = " " * map_indent + "║"
            for player in p.players_list:
                map_row += player.map[map_row_count] + "║"
            if map_row_count < len(p3_controls):
                map_row += p3_controls[map_row_count]
            print(map_row)
        printHUD(75)
