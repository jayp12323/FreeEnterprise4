import collections
import json
import os

with open("../f4c/dump.triggers.f4c", 'r') as file:
    triggers = file.read().splitlines()
with open("../f4c/dump.mapinfo.f4c", 'r') as file:
    mapinfos = file.read().splitlines()
with open("../f4c/dump.mapgrids.f4c", 'r') as file:
    mapgrids = file.read().splitlines()
with open("../f4c/dump.tilesets.f4c", 'r') as file:
    tilesets = file.read().splitlines()

master_map = collections.defaultdict(dict)
master_map["maps"] = collections.defaultdict(dict)


def return_tilesets(master_map):
    tileset = []
    tileset_name = ""
    start = 0
    for line in tilesets:
        if not line or line.startswith(" //") or line.startswith("{") or line.startswith("}"):
            continue
        if 'tileset(' in line:
            if start == 1:
                master_map["tilesets"][tileset_name] = tileset
            tileset_name = line.split("(")[1].split(")")[0]
            tileset = []
            start = 1
        else:
            if "warp" not in line:
                continue
            tile_code = line.strip().split()[0]
            tileset.append(tile_code[1:])
    return master_map


def return_mapinfo(master_map):
    mapinfo = []
    mapinfo_name = ""
    start = 0
    for line in mapinfos:
        if 'map(' in line:
            if start == 1:
                tileset_id = mapinfo[0].split()[1]
                master_map["maps"][mapinfo_name]["tileset_id"] = tileset_id
                try:
                    master_map["maps"][mapinfo_name]["warp_tile_ids"] = master_map["tilesets"][tileset_id]
                except:
                    master_map["maps"][mapinfo_name]["warp_tile_ids"] = []

            mapinfo_name = line.split("(")[1].split(")")[0]
            mapinfo = []
            start = 1
        else:
            if "tileset" not in line:
                continue
            mapinfo.append(line.strip())
    return master_map


def return_mapgrids(master_map):
    mapgrid = []
    mapgrid_names = []
    start = 0
    for line in mapgrids:
        if line.startswith(" //") or "{" in line or "}" in line:
            continue
        if 'mapgrid' in line:
            if start == 1:
                for name in mapgrid_names:
                    if name:
                        master_map["maps"][name]["mapgrid"] = mapgrid
                        warp_tile_ids = master_map["maps"][name]["warp_tile_ids"]
                        if warp_tile_ids:
                            master_map["maps"][name]["warp_tiles"] = []
                            for j, y in enumerate(mapgrid):
                                for i, x in enumerate(mapgrid[j]):
                                    if mapgrid[j][i] in warp_tile_ids:
                                        master_map["maps"][name]["warp_tiles"].append((i, j))

            mapgrid_names = line.split("/")[2].strip().split(" ")
            mapgrid = []
            start = 1
        else:
            if line:
                mapgrid.append(line.strip()[0:95].split())
    return master_map


master_map = return_tilesets(master_map)
master_map = return_mapinfo(master_map)
master_map = return_mapgrids(master_map)

for map in master_map["maps"]:
    try:
        if master_map["maps"][map]['warp_tiles']:
            print(map,master_map["maps"][map]['warp_tiles'])
    except:
        pass

    #         if start == 1:
#             if "teleport" in trigger[3]:
#                 loc, number = trigger[0].split("#")[1].strip(")").split(" ")
#                 loc = "#" + loc
#                 x, y = trigger[2].split(" ")[1:]
#                 target = trigger[3].split(" ")
#                 target_loc = target[1]
#                 target_x = target[3]
#                 target_y = target[4]
#                 try:
#                     facing = target[6]
#                 except IndexError:
#                     facing = ""
#                 if target_loc in ["#Overworld", "#Underworld", "#Moon"]:
#                     door_type = "exit"
#                 elif loc in ["#Overworld", "#Underworld", "#Moon"]:
#                     door_type = "entrance"
#                 elif loc in towns:
#                     door_type = "town_building"
#                 elif target_loc in towns:
#                     if loc in ["#CaveOfSummons3F"]:
#                         door_type = "town_building"
#                     else:
#                         door_type = "return"
#                 elif target_loc == '#BabilB1' and loc == '#CaveEblanExit':
#                     door_type = "town_building"
#
#                 elif target_loc == '#CaveEblanExit' and loc == '#BabilB1':
#                     door_type = "exit"
#                 elif loc == "#SylvanCaveYangRoom":
#                     door_type = "return"
#                 elif target_loc in ["#SylvanCaveYangRoom","#FabulInn",'#FabulEquipment','#FabulWestTower1F',
#                                     "#ToroiaCastleHospital","#ToroiaCastleStairs","#CaveEblanEquipment","#CaveEblanInn"]:
#                     door_type = "town_building"
#                 else:
#                     print([loc, number, x, y, target_loc, target_x, target_y,])
#
#                     door_type = "interior"
#                 if door_type != "interior":
#                     if target_loc in ["#Overworld", "#Underworld", "#Moon"] and loc in ["#LunarPassage1",
#                                                                                         "#LunarPassage2", "#MistCave",
#                                                                                         "#Mist"]:
#                         if number in ["4", "1"]:
#                             facing = "up"
#                         elif number == "7":
#                             facing = "right"
#                         elif number == "8":
#                             facing = "left"
#                         else:
#                             facing = "down"
#                     triggers.append(
#                         [loc, number, x, y, target_loc, target_x, target_y, facing, door_type,
#                          f"{loc}_{target_loc}_{facing}",
#                          map_key[target_loc]])
#         trigger = [line]
#         start = 1
#     else:
#         trigger.append(line)


overworld = ['#AdamantGrotto', '#Agart', '#AgartArmor', '#AgartInn', '#AgartWeapon', '#AgartWell', '#AntlionCave1F',
             '#AstroTower', '#BaronCastle', '#BaronChocoboForest', '#BaronEquipment', '#BaronInn', '#BaronSerpentRoad',
             '#BaronTown', '#BaronTownItems', '#BlackChocoboForest', '#CaveEblanEntrance', '#CaveMagnes1F', '#CidHouse',
             '#Damcyan', '#Eblan', '#Fabul', '#FabulChocoboForest', '#GiantMouth', '#HouseOfWishes',
             '#IslandChocoboForest', '#Kaipo', '#KaipoArmor', '#KaipoHospital', '#KaipoInn', '#KaipoWeapon', '#Mist',
             '#MistArmor', '#MistCave', '#MistInn', '#MistWeapon', '#MountHobsEast', '#MountHobsWest',
             '#MountOrdeals1F', '#MountOrdealsChocoboForest', '#Mysidia', '#MysidiaArmor', '#MysidiaCafe',
             '#MysidiaItem', '#MysidiaSerpentRoad', '#MysidiaWeapon', '#RoomToSewer', '#RosaHouse', '#RydiaHouse',
             '#Silvera', '#SilveraArmor', '#SilveraInn', '#SilveraItems', '#SilveraWeapons', '#ToroiaArmor',
             '#ToroiaCafe', '#ToroiaCastle', '#ToroiaInn', '#ToroiaItem', '#ToroiaStable', '#ToroiaTown',
             '#ToroiaWeapon', '#TrainingRoomMain', '#TroiaChocoboForest', '#Waterfall2F', '#WaterfallEntrance',
             '#WateryPass1F', '#WateryPass5F', "#Overworld", '#SoldierAirship', "#FabulInn", '#FabulEquipment',
             '#FabulWestTower1F', '#BabilB1', '#CaveEblanExit', "#ToroiaCastleHospital", "#ToroiaCastleStairs",
             "#CaveEblanEquipment", "#CaveEblanInn"]
underworld = ['#Babil1F', '#CaveOfSummons1F', '#CaveOfSummons3F', '#DwarfCastle', '#DwarfCastleBasement',
              '#SealedCaveEntrance',
              '#SmithyHouse', '#SylvanCave1F', '#SylvanCaveYangRoom', '#Tomra', '#TomraEquipment', '#TomraInn',
              '#TomraInn', '#TomraItem',
              '#TomraTreasury', "#Underworld", "#FeymarchTreasury", "#Feymarch1F", "#Feymarch2F", "#FeymarchSaveRoom",
              "#FeymarchLibrary1F", "#FeymarchWeapon",
              '#FeymarchArmor', '#FeymarchInn']

moon = ['#Bahamut1F', '#Hummingway', '#LunarPalaceLobby', '#LunarPassage1', '#LunarPassage2', "#Moon"]

map_key = {}
for i in overworld:
    map_key[i] = "#Overworld"
for i in underworld:
    map_key[i] = "#Underworld"
for i in moon:
    map_key[i] = "#Moon"

# trigger = ""
# start = 0
# triggers = []
# towns = ['#BaronTown', '#Feymarch1F', '#Feymarch2F', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart',
#          '#Tomra']
# for line in triggers:
#     line = line.strip()
#     print(line)
#     if "trigger" in line:
#         if start == 1:
#             if "teleport" in trigger[3]:
#                 loc, number = trigger[0].split("#")[1].strip(")").split(" ")
#                 loc = "#" + loc
#                 x, y = trigger[2].split(" ")[1:]
#                 target = trigger[3].split(" ")
#                 target_loc = target[1]
#                 target_x = target[3]
#                 target_y = target[4]
#                 try:
#                     facing = target[6]
#                 except IndexError:
#                     facing = ""
#                 if target_loc in ["#Overworld", "#Underworld", "#Moon"]:
#                     door_type = "exit"
#                 elif loc in ["#Overworld", "#Underworld", "#Moon"]:
#                     door_type = "entrance"
#                 elif loc in towns:
#                     door_type = "town_building"
#                 elif target_loc in towns:
#                     if loc in ["#CaveOfSummons3F"]:
#                         door_type = "town_building"
#                     else:
#                         door_type = "return"
#                 elif target_loc == '#BabilB1' and loc == '#CaveEblanExit':
#                     door_type = "town_building"
#
#                 elif target_loc == '#CaveEblanExit' and loc == '#BabilB1':
#                     door_type = "exit"
#                 elif loc == "#SylvanCaveYangRoom":
#                     door_type = "return"
#                 elif target_loc in ["#SylvanCaveYangRoom","#FabulInn",'#FabulEquipment','#FabulWestTower1F',
#                                     "#ToroiaCastleHospital","#ToroiaCastleStairs","#CaveEblanEquipment","#CaveEblanInn"]:
#                     door_type = "town_building"
#                 else:
#                     print([loc, number, x, y, target_loc, target_x, target_y,])
#
#                     door_type = "interior"
#                 if door_type != "interior":
#                     if target_loc in ["#Overworld", "#Underworld", "#Moon"] and loc in ["#LunarPassage1",
#                                                                                         "#LunarPassage2", "#MistCave",
#                                                                                         "#Mist"]:
#                         if number in ["4", "1"]:
#                             facing = "up"
#                         elif number == "7":
#                             facing = "right"
#                         elif number == "8":
#                             facing = "left"
#                         else:
#                             facing = "down"
#                     triggers.append(
#                         [loc, number, x, y, target_loc, target_x, target_y, facing, door_type,
#                          f"{loc}_{target_loc}_{facing}",
#                          map_key[target_loc]])
#         trigger = [line]
#         start = 1
#     else:
#         trigger.append(line)
# DB_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'db')
# COLUMNS = ['map', 'trigger_number', 'x', 'y', 'dest', 'dest_x', 'dest_y', 'facing', 'type', "name", "world"]
