import csv
import os

with open("../f4c/dump.triggers.f4c", 'r') as file:
    lines = file.read().splitlines()
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
             '#WateryPass1F', '#WateryPass5F', "#Overworld", '#SoldierAirship']
underworld = ['#Babil1F', '#CaveOfSummons1F', '#DwarfCastle', '#DwarfCastleBasement', '#SealedCaveEntrance',
              '#SmithyHouse', '#SylvanCave1F', '#Tomra', '#TomraEquipment', '#TomraInn', '#TomraInn', '#TomraItem',
              '#TomraTreasury', "#Underworld","#Feymarch2F","#FeymarchSaveRoom","#FeymarchLibrary1F","#FeymarchWeapon",
              '#FeymarchArmor','#FeymarchInn']

moon = ['#Bahamut1F', '#Hummingway', '#LunarPalaceLobby', '#LunarPassage1', '#LunarPassage2', "#Moon"]

map_key = {}
for i in overworld:
    map_key[i] = "#Overworld"
for i in underworld:
    map_key[i] = "#Underworld"
for i in moon:
    map_key[i] = "#Moon"

trigger = ""
start = 0
triggers = []
towns = ['#BaronTown', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart', '#Tomra']
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
                    door_type = "return"
                elif loc=="#Feymarch2F":
                    door_type = "town_building"
                else:
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
                    triggers.append(
                        [loc, number, x, y, target_loc, target_x, target_y, facing, door_type,
                         f"{loc}_{target_loc}_{facing}",
                         map_key[target_loc]])
        trigger = [line]
        start = 1
    else:
        trigger.append(line)
DB_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'db')
COLUMNS = ['map', 'trigger_number', 'x', 'y', 'dest', 'dest_x', 'dest_y', 'facing', 'type', "name", "world"]

to_remove = ["#SoldierAirship", "#GiantMouth", "#MysidiaSerpentRoad","#BaronSerpentRoad", '#BlackChocoboForest',
             '#AdamantGrotto', '#CaveEblanEntrance',"#TrainingRoomMain","#RoomToSewer"]


for map_to_remove in to_remove:
    for trigger in list(triggers):
        if map_to_remove == trigger[4] or map_to_remove == trigger[0]:
            triggers.remove(trigger)

hardcoded = [["#Underworld", "5", "48", "15", "#Babil1F", "15", "24", "up", "entrance", "#Underworld_#Babil1F_up",
              "#Underworld"],
             ["#Underworld", "6", "49", "15", "#Babil1F", "15", "24", "up", "entrance", "#Underworld_#Babil1F_up",
              "#Underworld"],
             ["#Silvera", "7", "17", "31", "#Overworld", "210", "130", "", "exit", "#Silvera_#Overworld_",
              "#Overworld"],
             ["#ToroiaTown", "11", "16", "29", "#Overworld", "36", "83", "", "exit", "#ToroiaTown_#Overworld_",
              "#Overworld"],
             ["#CaveOfSummons1F", "5", "17", "9", "#Underworld", "27", "86", "", "exit", "#CaveOfSummons1F_#Underworld_",
              "#Underworld"]
             ]

triggers += hardcoded
with open(os.path.join(DB_PATH, 'doors.csvdb'), 'w', newline='') as file:
    csv_file = csv.writer(file)
    csv_file.writerow(COLUMNS)
    csv_file.writerows(triggers)
