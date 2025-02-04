import collections
import csv
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

overworld = ["#CaveEblanEquipment", "#CaveEblanInn", "#FabulInn", "#Overworld", "#ToroiaCastleHospital",
             "#ToroiaCastleStairs", '#AdamantGrotto', '#Agart', '#AgartArmor', '#AgartInn', '#AgartWeapon',
             '#AgartWell', '#AntlionCave1F', '#AstroTower', '#BabilB1', '#BaronCastle', '#BaronCastleEastTower1F',
             '#BaronCastleEastTower2F', '#BaronCastleEastTowerB1', '#BaronCastlePrisonEntrance',
             '#BaronCastleSoldiersQuarters', '#BaronChocoboForest', '#BaronEquipment', '#BaronInn', '#BaronSerpentRoad',
             '#BaronTown', '#BaronTownItems', '#BlackChocoboForest', '#CaveEblanEntrance', '#CaveEblanExit',
             '#CaveMagnes1F', '#CaveMagnes2F', '#CaveMagnes3F', '#CaveMagnes4F', '#CaveMagnes5F', '#CidHouse',
             '#Damcyan', '#Damcyan1F', '#Damcyan2F', '#DamcyanTreasuryEntrance', '#Eblan', '#Eblan1F', '#Eblan2F',
             '#EblanEastTower1F', '#EblanEastTower2F', '#EblanThroneRoom', '#EblanWestTower1F', '#EblanWestTower2F',
             '#Fabul', '#FabulChocoboForest', '#FabulEquipment', '#FabulHospital', '#FabulWestTower1F', '#GiantMouth',
             '#HouseOfWishes', '#IslandChocoboForest', '#Kaipo', '#KaipoArmor', '#KaipoHospital', '#KaipoInn',
             '#KaipoWeapon', '#Mist', '#MistArmor', '#MistCave', '#MistInn', '#MistWeapon', '#MountHobsEast',
             '#MountHobsWest', '#MountOrdeals1F', '#MountOrdealsChocoboForest', '#Mysidia', '#MysidiaArmor',
             '#MysidiaCafe', '#MysidiaItem', '#MysidiaSerpentRoad', '#MysidiaWeapon', '#RoomToSewer', '#RosaHouse',
             '#RydiaHouse', '#Silvera', '#SilveraArmor', '#SilveraInn', '#SilveraItems', '#SilveraWeapons',
             '#SoldierAirship', '#ToroiaArmor', '#ToroiaCafe', '#ToroiaCastle', '#ToroiaCastleHall',
             '#ToroiaCastleStairs', '#ToroiaInn', '#ToroiaItem', '#ToroiaStable', '#ToroiaTown', '#ToroiaWeapon',
             '#TrainingRoomMain', '#TrainingRoomMain', '#TroiaChocoboForest', '#Waterfall2F', '#WaterfallEntrance',
             '#WateryPass1F', '#WateryPass5F', '#Zot2F', '#Zot3F', '#Zot4F', '#Zot5F', '#Zot6F']
underworld = ["#Feymarch1F", "#Feymarch2F", "#FeymarchLibrary1F", "#FeymarchSaveRoom", "#FeymarchTreasury",
              "#FeymarchWeapon", "#Underworld", '#Babil1F', '#Babil4F', '#BabilFloorAirship2', '#BabilFloorIceMail',
              '#BabilFloorIceMail2', '#CaveOfSummons1F', '#CaveOfSummons2F', '#CaveOfSummons3F', '#DwarfCastle',
              '#DwarfCastleBasement', '#DwarfCastleCrystalRoom', '#DwarfCastleTower2F', '#Feymarch1F', '#Feymarch2F',
              '#FeymarchArmor', '#FeymarchInn', '#FeymarchLibrary1F', '#FeymarchLibrary2F', '#FeymarchTreasury',
              '#SealedCave1F', '#SealedCave2F', '#SealedCave3F', '#SealedCave4F', '#SealedCave5F', '#SealedCave6F',
              '#SealedCave7F', '#SealedCaveCrystalRoom', '#SealedCaveDemonWallRoom', '#SealedCaveEntrance',
              '#SealedCaveSaveRoom', '#SmithyHouse', '#SmithyHouseMainFloor', '#SylvanCave1F', '#SylvanCave2F',
              '#SylvanCave3F', '#SylvanCaveYangRoom', '#Tomra', '#TomraEquipment', '#TomraInn', '#TomraItem',
              '#TomraTreasury']

moon = ['#Bahamut1F', '#Hummingway', '#LunarPalaceLobby', '#LunarPassage1', '#LunarPassage2', "#Moon", '#Bahamut2F',
        '#LunarSubterran1F', '#LunarSubterran2F', '#LunarSubterran3F', '#LunarSubterran4F', '#LunarSubterran5F',
        '#LunarSubterran6F', '#LunarSubterran7F', '#LunarCore1F', '#LunarCore2F', '#LunarCore3F', '#LunarCore4F',
        '#LunarSubterranTunnelCure3', '#LunarSubterranTunnelProtectRing', '#LunarSubterranTunnelWhiteRobe',
        '#LunarSubterranSaveRoom1', '#LunarSubterranTunnelMinerva']

map_key = {}
for i in overworld:
    map_key[i] = "#Overworld"
for i in underworld:
    map_key[i] = "#Underworld"
for i in moon:
    map_key[i] = "#Moon"


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
                        master_map["maps"][name]["mapgrid_id"] = map_grid_id
                        warp_tile_ids = master_map["maps"][name]["warp_tile_ids"]
                        if warp_tile_ids:
                            master_map["maps"][name]["warp_tiles"] = []
                            for j, y in enumerate(mapgrid):
                                for i, x in enumerate(mapgrid[j]):
                                    if mapgrid[j][i] in warp_tile_ids:
                                        master_map["maps"][name]["warp_tiles"].append((i, j))

            mapgrid_names = line.split("/")[2].strip().split(" ")
            map_grid_id = line.split("(")[1].split(")")[0]
            mapgrid = []
            start = 1
        else:
            if line:
                mapgrid.append(line.strip()[0:95].split())
    return master_map


def return_triggers(master_map):
    trigger_map = collections.defaultdict(dict)
    trigger = ""
    start = 0
    for line in triggers:
        line = line.strip()
        if "trigger" in line:
            if start == 1:
                loc, number = trigger[0].split("#")[1].strip(")").split(" ")
                loc = "#" + loc
                if loc not in trigger_map:
                    trigger_map[loc]["triggers"] = []
                    trigger_map[loc]["last_trigger_num"] = 0
                trigger_map[loc]["last_trigger_num"] = int(trigger[0].split(" ")[1][:-1])
                if "teleport" in trigger[3]:
                    x, y = trigger[2].split(" ")[1:]
                    x = int(x)
                    y = int(y)
                    target = trigger[3].split(" ")
                    target_loc = target[1]
                    target_x = int(target[3])
                    target_y = int(target[4])
                    try:
                        trigger_map[loc]["triggers"].append(
                            {(x, y): [target_loc, target_x, target_y, master_map["maps"][loc]["mapgrid"][y][x]]})
                    except:
                        trigger_map[loc]["triggers"].append(
                            {(x, y): [target_loc, target_x, target_y,'']})

            trigger = [line]
            start = 1
        else:
            trigger.append(line)
    for map in trigger_map:
        master_map["maps"][map]["triggers"] = trigger_map[map]["triggers"]
        master_map["maps"][map]["last_trigger_num"] = trigger_map[map]["last_trigger_num"]
    return master_map


def map_trigger_to_warp(master_map):
    warps_to_map = collections.defaultdict(dict)
    warps_to_map["warps"] = []
    for map in master_map["maps"]:
        if 'warp_tiles' in master_map["maps"][map]:
            warps_to_map[map]["warps"] = []
            if 'triggers' in master_map["maps"][map] and master_map["maps"][map]['triggers'] != [] and \
                    master_map["maps"][map]['warp_tiles']:
                for warp in master_map["maps"][map]['warp_tiles']:
                    warps_to_map[map]["warps"].append(warp)
    for map in master_map["maps"]:
        min_val = 1
        # if "Eblan" in map:
        #     min_val = 3
        if "triggers" not in master_map["maps"][map]:
            continue
        for trigger_map in master_map["maps"][map]["triggers"]:
            for trigger in trigger_map:
                trigger_dest, x, y,trigger_tile_id = trigger_map[trigger]
                if "warps" not in warps_to_map[trigger_dest] or not warps_to_map[trigger_dest]["warps"]:
                    continue
                for x_dest, y_dest in warps_to_map[trigger_dest]["warps"]:
                    if "warp_to_trigger" not in warps_to_map[trigger_dest]:
                        warps_to_map[trigger_dest]["warp_to_trigger"] = {}

                    if x == x_dest and abs(y_dest - y) == 3:
                        warps_to_map[trigger_dest]["warp_to_trigger"][(x_dest, y_dest)] = [map, trigger[0], trigger[1],trigger_tile_id]
                    else:
                        abs_value = abs(x_dest - x) + abs(y_dest - y)
                        if abs_value <= min_val:
                            warps_to_map[trigger_dest]["warp_to_trigger"][(x_dest, y_dest)] = [map, trigger[0],
                                                                                               trigger[1],trigger_tile_id]

    return warps_to_map


master_map = return_tilesets(master_map)
master_map = return_mapinfo(master_map)
master_map = return_mapgrids(master_map)
master_map = return_triggers(master_map)

warps_to_map = map_trigger_to_warp(master_map)

mapgrid_to_replace=[]
db=[]
for map in warps_to_map:

    "mapgrid ($04 17 31) { 7C }"


    if "warp_to_trigger" in warps_to_map[map]:
        master_map_object = master_map["maps"][map]
        last_trigger = master_map_object["last_trigger_num"]
        for warp_trigger in warps_to_map[map]["warp_to_trigger"]:
            last_trigger+=1
            dest,x,y,tile_id=warps_to_map[map]["warp_to_trigger"][warp_trigger]
            mapgrid_id=master_map_object["mapgrid_id"]

            if not tile_id:
                if mapgrid_id  in ['$8C','$100','$136','$144','$145','$15A']:
                    tile_id='72'
                elif mapgrid_id=='$160':
                    tile_id='6E'
                else:
                    tile_id="7C"
            # map, trigger_number, x, y, dest, dest_x, dest_y, facing, type, name, world

            mapgrid_to_replace.append("mapgrid ({} {} {}) {{ {} }}".format(master_map["maps"][map]["mapgrid_id"], warp_trigger[0],warp_trigger[1],tile_id ))
            db.append([map,last_trigger,warp_trigger[0],warp_trigger[1],dest,x,y,"up","exit","{}_{}_{}_{}".format(map,dest,"up",last_trigger),map_key[map]])

            # print(map, warp_trigger, warps_to_map[map]["warp_to_trigger"][warp_trigger])
for m in mapgrid_to_replace:
    print(m)

for d in db:
    print(d)


lines=list(triggers)

trigger = ""
start = 0
triggers = []
towns = ['#BaronTown', '#Feymarch1F', '#Feymarch2F', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart',
         '#Tomra']
for line in lines:
    line = line.strip()
    if "trigger" in line:
        if start == 1:
            if "teleport" in trigger[3]:
                loc, number = trigger[0].split("#")[1].strip(")").split(" ")
                loc = "#" + loc
                x, y = trigger[2].split(" ")[1:]
                target = trigger[3].split(" ")
                target_loc = target[1]
                target_x = target[3]
                target_y = target[4]
                try:
                    facing = target[6]
                except IndexError:
                    facing = ""
                if target_loc in ["#Overworld", "#Underworld", "#Moon"]:
                    door_type = "exit"
                elif loc in ["#Overworld", "#Underworld", "#Moon"]:
                    door_type = "entrance"
                elif loc in towns:
                    door_type = "town_building"
                elif target_loc in towns:
                    if loc in ["#CaveOfSummons3F"]:
                        door_type = "town_building"
                    else:
                        door_type = "return"
                elif target_loc == '#BabilB1' and loc == '#CaveEblanExit':
                    door_type = "town_building"

                elif target_loc == '#CaveEblanExit' and loc == '#BabilB1':
                    door_type = "exit"
                elif loc == "#SylvanCaveYangRoom":
                    door_type = "return"
                elif target_loc in ["#SylvanCaveYangRoom","#FabulInn",'#FabulEquipment','#FabulWestTower1F',
                                    "#ToroiaCastleHospital","#ToroiaCastleStairs","#CaveEblanEquipment","#CaveEblanInn"]:
                    door_type = "town_building"
                else:
                    print([loc, number, x, y, target_loc, target_x, target_y,])

                    door_type = "interior"
                if door_type != "interior":
                    if target_loc in ["#Overworld", "#Underworld", "#Moon"] and loc in ["#LunarPassage1",
                                                                                        "#LunarPassage2", "#MistCave",
                                                                                        "#Mist"]:
                        if number in ["4", "1"]:
                            facing = "up"
                        elif number == "7":
                            facing = "right"
                        elif number == "8":
                            facing = "left"
                        else:
                            facing = "down"
                    if not facing:
                        facing="up"
                    triggers.append(
                        [loc, number, x, y, target_loc, target_x, target_y, facing, door_type,
                         f"{loc}_{target_loc}_{facing}_{number}",
                         map_key[target_loc]])
        trigger = [line]
        start = 1
    else:
        trigger.append(line)
DB_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'db')
COLUMNS = ['map', 'trigger_number', 'x', 'y', 'dest', 'dest_x', 'dest_y', 'facing', 'type', "name", "world"]

to_remove = ["#SoldierAirship", "#GiantMouth", "#MysidiaSerpentRoad", "#BaronSerpentRoad",
             "#TrainingRoomMain"]

for map_to_remove in to_remove:
    for trigger in list(triggers):
        if map_to_remove == trigger[4] :
            triggers.remove(trigger)
        elif map_to_remove == trigger[0]:
            triggers.remove(trigger)
        elif "#SylvanCaveYangRoom" == trigger[4] and "#SylvanCaveYangRoom" == trigger[0]:
            triggers.remove(trigger)
        # elif "#Underworld" == trigger[4] and "#SylvanCaveYangRoom" == trigger[0]:
        #     triggers.remove(trigger)

hardcoded = [["#Underworld", "5", "48", "15", "#Babil1F", "15", "24", "up", "entrance", "#Underworld_#Babil1F_up",
              "#Underworld"],
             ["#Underworld", "6", "49", "15", "#Babil1F", "15", "24", "up", "entrance", "#Underworld_#Babil1F_up",
              "#Underworld"],
             ]


triggers += hardcoded
triggers += db
with open(os.path.join(DB_PATH, 'floors.csvdb'), 'w', newline='') as file:
    csv_file = csv.writer(file)
    csv_file.writerow(COLUMNS)
    csv_file.writerows(triggers)
