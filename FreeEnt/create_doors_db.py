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
             '#WateryPass1F', '#WateryPass5F', "#Overworld", '#SoldierAirship',"#FabulInn",'#FabulEquipment',
             '#FabulWestTower1F','#BabilB1', '#CaveEblanExit',"#ToroiaCastleHospital","#ToroiaCastleStairs","#CaveEblanEquipment","#CaveEblanInn"]
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
             ["#Silvera", "7", "17", "31", "#Overworld", "210", "130", "", "exit", "#Silvera_#Overworld_",
              "#Overworld"],
             ["#ToroiaTown", "11", "16", "29", "#Overworld", "36", "83", "", "exit", "#ToroiaTown_#Overworld_",
              "#Overworld"],
             ["#CaveOfSummons1F", "5", "17", "9", "#Underworld", "27", "86", "", "exit",
              "#CaveOfSummons1F_#Underworld_",
              "#Underworld"],
             ["#Feymarch1F", "7", "12", "14", "#CaveOfSummons3F", "18", "14", "up", "exit",
              "#Feymarch1F_#CaveOfSummons3F_up",
              "#Underworld"],
             ["#FeymarchTreasury", "4", "16", "21", "#Feymarch1F", "19", "15", "up", "return",
              "#FeymarchTreasury_#Feymarch1F_up",
              "#Underworld"],
             ["#Feymarch2F", "5", "28", "11", "#Feymarch1F", "14", "4", "up", "exit", "#Feymarch2F_#Feymarch1F_up",
              "#Underworld"],
             ["#SylvanCaveYangRoom", "4", "11", "10", "#SylvanCave3F", "21", "19", "up", "return",
              "#SylvanCaveYangRoom_#SylvanCave3F_up",
              "#Underworld"],
             ["#SylvanCave1F", "12", "16", "1", "#Underworld", "13", "14", "", "exit", "#SylvanCave1F_#Underworld_",
              "#Underworld"],
             ["#LunarPalaceLobby", "4", "16", "29", "#Moon", "28", "26", "", "exit", "#LunarPalaceLobby_#Moon_",
              "#Moon"],
             ]

non_randomized = [["#CaveOfSummons3F", "7", "11", "1", "#CaveOfSummons2F", "28", "16", "up", "non_randomized",
                   "#CaveOfSummons3F_#CaveOfSummons2F_up",
                   "#Underworld"],
                  ["#CaveOfSummons2F", "3", "4", "18", "#CaveOfSummons1F", "3", "17", "up", "non_randomized",
                   "#CaveOfSummons2F_#CaveOfSummons1F_up",
                   "#Underworld"],
                  ["#SylvanCave3F", "7", "5", "6", "#SylvanCave2F", "4", "8", "up", "non_randomized",
                   "#SylvanCave3F_#SylvanCave2F_up",
                   "#Underworld"],
                  ["#SylvanCave2F", "15", "6", "26", "#SylvanCave1F", "7", "29", "up", "non_randomized",
                   "#SylvanCave2F_#SylvanCave1F_up",
                   "#Underworld"],
                  ["#SylvanCave1F", "13", "16", "27", "#SylvanCave2F", "14", "25", "up", "non_randomized",
                   "#SylvanCave1F_#SylvanCave2F_up",
                   "#Underworld"],
                  ["#SylvanCave2F", "16", "17", "17", "#SylvanCave1F", "16", "19", "up", "non_randomized",
                   "#SylvanCave2F_#SylvanCave1F_up",
                   "#Underworld"],
                  ]


triggers += hardcoded
triggers += non_randomized
with open(os.path.join(DB_PATH, 'doors.csvdb'), 'w', newline='') as file:
    csv_file = csv.writer(file)
    csv_file.writerow(COLUMNS)
    csv_file.writerows(triggers)
