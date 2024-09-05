import json

try:
    from . import databases
except ImportError:
    import databases

towns = {"#Overworld": ['#BaronTown', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart'],
         "#Underworld": ['#Tomra', '#Feymarch1F', "#Feymarch2F", "#CaveOfSummons1F", "#SylvanCave1F"], "#Moon": []}
towns_flat = ['#BaronTown', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart', '#Tomra',
              '#Feymarch1F', "#Feymarch2F", "#CaveOfSummons1F", "#SylvanCave1F"]

ki_location = {"RewardSlot.antlion_item": "#AntlionCave1F", "RewardSlot.babil_boss_item": "#Babil1F",
               "RewardSlot.bahamut_item": "#Bahamut1F", "RewardSlot.baron_castle_character": "#RoomToSewer",
               "RewardSlot.baron_castle_item": "#RoomToSewer", "RewardSlot.baron_inn_character": "#BaronInn",
               "RewardSlot.baron_inn_item": "#BaronInn", "RewardSlot.baron_throne_item": "#RoomToSewer",
               "RewardSlot.cannon_item": "#Babil1F", "RewardSlot.cave_eblan_character": "#CaveEblanEntrance",
               "RewardSlot.cave_eblan_chest": "#CaveEblanEntrance",
               "RewardSlot.cave_of_summons_chest": "#CaveOfSummons1F", "RewardSlot.damcyan_character": "#Damcyan",
               "RewardSlot.dwarf_castle_character": "#DwarfCastle|#DwarfCastleBasement",
               "RewardSlot.eblan_chest_1": "#Eblan", "RewardSlot.eblan_chest_2": "#Eblan",
               "RewardSlot.eblan_chest_3": "#Eblan", "RewardSlot.fabul_item": "#Fabul",
               "RewardSlot.feymarch_item": "#Feymarch1F", "RewardSlot.feymarch_king_item": "#FeymarchLibrary1F",
               "RewardSlot.feymarch_queen_item": "#FeymarchLibrary1F", "RewardSlot.forge_item": "#SmithyHouse",
               "RewardSlot.found_yang_item": "#SylvanCaveYangRoom&#Fabul", "RewardSlot.giant_character": "#Mysidia",
               "RewardSlot.giant_chest": "#Mysidia", "RewardSlot.hobs_character": "#MountHobsEast",
               "RewardSlot.kaipo_character": "#KaipoHospital", "RewardSlot.lower_babil_chest_1": "#Babil1F",
               "RewardSlot.lower_babil_chest_2": "#Babil1F", "RewardSlot.lower_babil_chest_3": "#Babil1F",
               "RewardSlot.lower_babil_chest_4": "#Babil1F",
               "RewardSlot.luca_item": "#DwarfCastle|#DwarfCastleBasement",
               "RewardSlot.lunar_boss_1_item": "#LunarPalaceLobby", "RewardSlot.lunar_boss_2_item": "#LunarPalaceLobby",
               "RewardSlot.lunar_boss_3_item": "#LunarPalaceLobby",
               "RewardSlot.lunar_boss_4_item_1": "#LunarPalaceLobby",
               "RewardSlot.lunar_boss_4_item_2": "#LunarPalaceLobby",
               "RewardSlot.lunar_boss_5_item": "#LunarPalaceLobby",
               "RewardSlot.lunar_core_chest_1": "#LunarPalaceLobby",
               "RewardSlot.lunar_core_chest_2": "#LunarPalaceLobby",
               "RewardSlot.lunar_core_chest_3": "#LunarPalaceLobby",
               "RewardSlot.lunar_core_chest_4": "#LunarPalaceLobby",
               "RewardSlot.lunar_core_chest_5": "#LunarPalaceLobby",
               "RewardSlot.lunar_core_chest_6": "#LunarPalaceLobby",
               "RewardSlot.lunar_core_chest_7": "#LunarPalaceLobby",
               "RewardSlot.lunar_core_chest_8": "#LunarPalaceLobby",
               "RewardSlot.lunar_core_chest_9": "#LunarPalaceLobby",
               "RewardSlot.lunar_palace_character": "#LunarPalaceLobby",
               "RewardSlot.lunar_path_chest": "#LunarPassage1", "RewardSlot.magnes_item": "#CaveMagnes1F",
               "RewardSlot.mist_character": "#Mist&#KaipoInn", "RewardSlot.mysidia_character_1": "#HouseOfWishes",
               "RewardSlot.mysidia_character_2": "#HouseOfWishes", "RewardSlot.ordeals_character": "#MountOrdeals1F",
               "RewardSlot.ordeals_item": "#MountOrdeals1F", "RewardSlot.pan_trade_item": "#SylvanCaveYangRoom&#Fabul",
               "RewardSlot.pink_trade_item": "#AdamantGrotto", "RewardSlot.rat_trade_item": "#AdamantGrotto",
               "RewardSlot.rydias_mom_item": "#Mist", "RewardSlot.sealed_cave_item": "#SealedCaveEntrance",
               "RewardSlot.starting_character": "None", "RewardSlot.starting_item": "None",
               "RewardSlot.starting_partner_character": "None", "RewardSlot.sylph_cave_chest_1": "#SylvanCave1F",
               "RewardSlot.sylph_cave_chest_2": "#SylvanCave1F", "RewardSlot.sylph_cave_chest_3": "#SylvanCave1F",
               "RewardSlot.sylph_cave_chest_4": "#SylvanCave1F", "RewardSlot.sylph_cave_chest_5": "#SylvanCave1F",
               "RewardSlot.sylph_cave_chest_6": "#SylvanCave1F", "RewardSlot.sylph_cave_chest_7": "#SylvanCave1F",
               "RewardSlot.sylph_item": "#SylvanCaveYangRoom", "RewardSlot.upper_babil_chest": "#ToroiaCastle",
               "RewardSlot.watery_pass_character": "#WateryPass1F|#WateryPass5F",
               "RewardSlot.zot_character_1": "#ToroiaCastle", "RewardSlot.zot_character_2": "#ToroiaCastle",
               "RewardSlot.zot_chest": "#ToroiaCastle", "RewardSlot.zot_item": "#ToroiaCastle",
               "RewardSlot.fixed_crystal":"#LunarPalaceLobby"}

DIRECTION_MAP = {
    'up': 0,
    'right': 1,
    'down': 2,
    'left': 3,
}


def map_exit_to_entrance(remapped_entrances, exit):
    try:
        entrance_key = f"{exit[4]}_{exit[0]}_{exit[7]}"
    except IndexError:
        entrance_key = f"{exit[4]}_{exit[0]}_"
    for i in remapped_entrances:
        if i[10] == entrance_key:
            return [i[0]] + i[2:4] + [i[12]]
    entrance_key_up = f"{exit[4]}_{exit[0]}_up"
    for i in remapped_entrances:
        if i[10] == entrance_key_up:
            return [i[0]] + i[2:4] + [i[12]]
    entrance_key_down = f"{exit[4]}_{exit[0]}_down"
    for i in remapped_entrances:
        if i[10] == entrance_key_down:
            return [i[0]] + i[2:4] + [i[12]]

    # print(exit)
    return ""


def shuffle_locations(rnd, entrances, exits):
    towns_ = towns
    entrance_destinations = [entrance[4:] for entrance in entrances]
    exit_dict = {}
    for dest in entrance_destinations:
        exit_tup = (dest[0], dest[3])
        if exit_tup not in exit_dict:
            exit_dict[exit_tup] = dest[1:]

    exit__ = [[list(i)[0]] + exit_dict[i] + [list(i)[1]] for i in exit_dict]
    rnd.shuffle((exit__))
    shuffled_exits = list(exit__)
    exit_dict = {}
    rnd.shuffle(shuffled_exits)
    overworld_entrances = 0
    # print("max_towns", world, max_towns_in_overworld)
    tries = 0
    while exit__:
        if tries > 20:
            return False
        exit___ = exit__.pop(0)
        shuffled_exit = shuffled_exits.pop(0)
        if shuffled_exit[0] in towns_ and shuffled_exit[4] == 'entrance' and exit___[4] == "entrance":
            overworld_entrances += 1

        if (shuffled_exit[0] in towns_ and shuffled_exit[4] == 'entrance' and exit___[5].split("_")[0] ==
            shuffled_exit[0]) or (
                shuffled_exit[0] == "#Feymarch2F" and shuffled_exit[4] == 'town_building' and exit___[5].split("_")[1]
                in ["#FeymarchTreasury", "#FeymarchSaveRoom", "#FeymarchLibrary1F", "#FeymarchWeapon", "#FeymarchArmor",
                    "#FeymarchInn"]) or (
                shuffled_exit[0] == "#SylvanCave1F" and exit___[5].split("_")[1] == "#SylvanCaveYangRoom") or (
                shuffled_exit[0] == "#CaveOfSummons1F" and exit___[5].split("_")[1] == "#Feymarch1F") or (
                shuffled_exit[0] == "#Feymarch1F" and exit___[5].split("_")[1] in ["#FeymarchTreasury",
                                                                                   "Feymarch2F"]):
            exit__ = [exit___] + exit__
            rnd.shuffle(exit__)
            shuffled_exits.append(shuffled_exit)
            rnd.shuffle(shuffled_exits)
            tries += 1
            continue
        exit_dict[tuple([exit___[0], exit___[3]])] = shuffled_exit
    remapped_entrances = []
    for entrance in entrances:
        exit_key = tuple([entrance[4], entrance[7]])
        remapped_exit = exit_dict[exit_key]
        remapped_entrances.append(entrance[0:4] + [entrance[-2]] + remapped_exit)

    remapped_exits = []
    for i in exits:
        entrance = map_exit_to_entrance(remapped_entrances, i)
        if not entrance:
            if "SylvanCaveTreasury" in i[0] or "#SylvanCave3F" in i[0]:
                entrance = map_exit_to_entrance(remapped_entrances, ["#SylvanCave1F", "", "", "", "#Underworld"])
            elif "CaveOfSummons3F" in i[0]:
                entrance = map_exit_to_entrance(remapped_entrances, ["#CaveOfSummons1F", "", "", "", "#Underworld"])

            elif i[0] == "#EblanBasement":
                entrance = map_exit_to_entrance(remapped_entrances, ["#Eblan", "", "", "", "#Overworld"])
            else:
                print("not found", i)
            # elif i[0] == "#FeymarchTreasury":
            #     entrance = map_exit_to_entrance(remapped_entrances, ["#CaveOfSummons1F", "", "", "", "#Underworld"])

        if entrance:
            remapped_exits.append(i[0:4] + [i[-2]] + entrance)
        else:
            print("not found")
            print(i)
    return [remapped_entrances, remapped_exits]


def find_all_paths(graph, start, end, type, path=[]):
    path = path + [start]
    if start in end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start][type]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, type, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths


def apply(env, rom_base, testing=False):
    doors_view = databases.get_doors_dbview()

    shuffled_entrances = {}
    shuffled_exits = {}
    spoil_entrances = {}

    # for i in ["#Overworld", "#Underworld", "#Moon"]:
    entrances = [list(i) for i in doors_view.find_all(
        lambda sp: (sp.type == "entrance" or sp.type == "town_building"))]
    exits = [list(i) for i in
             doors_view.find_all(lambda sp: (sp.type == "exit" or sp.type == "return"))]

    is_loop = False
    loop_count = 0
    tries = 1
    paths_to_world = {}
    graph = {}

    while not is_loop:
        graph = {}
        paths_to_world = {}
        spoil_entrances = []
        if loop_count > 200:
            return False
        loop_count += 1
        max_tries = 1000
        try:
            remapped_entrances, remapped_exits = shuffle_locations(env.rnd, entrances, exits)
        except TypeError:
            tries += 1
            if tries < max_tries:
                continue
            else:
                return False
        print("max locations took tries: ", tries)
        shuffled_entrances = remapped_entrances
        shuffled_exits = remapped_exits

        for j in remapped_entrances + remapped_exits:
            location = j[0]
            destination = j[5]
            if len(j) == 13:
                type = "entrances"
                message = f"{j[5]} is in the {j[4].split('_')[1]} location"
                if message not in spoil_entrances:
                    spoil_entrances.append(message)
            else:
                type = "exits"
            if location not in graph:
                graph[location] = {"entrances": [], "exits": []}
            if destination not in graph[location][type]:

                if "SylvanCave3F" in location and type == "entrances":
                    if "#SylvanCave1F" not in graph:
                        graph["#SylvanCave1F"] = {"entrances": [], "exits": []}
                    graph["#SylvanCave1F"][type].append(destination)
                    graph["#SylvanCave1F"][type].append("SylvanCave3F")
                if "CaveOfSummons3F" in location and type == "entrances":
                    if "#CaveOfSummons1F" not in graph:
                        graph["#CaveOfSummons1F"] = {"entrances": [], "exits": []}
                    graph["#CaveOfSummons1F"][type].append(destination)
                    graph["#CaveOfSummons1F"][type].append("CaveOfSummons3F")

                if "SylvanCave1F" in location and type == "exits":
                    if "#SylvanCave3F" not in graph:
                        graph["#SylvanCave3F"] = {"entrances": [], "exits": []}
                    graph["#SylvanCave3F"][type].append(destination)
                    graph["#SylvanCave3F"][type].append("SylvanCave1F")
                if "CaveOfSummons1F" in location and type == "exits":
                    if "#CaveOfSummons3F" not in graph:
                        graph["#CaveOfSummons3F"] = {"entrances": [], "exits": []}
                    graph["#CaveOfSummons3F"][type].append(destination)
                    graph["#CaveOfSummons3F"][type].append("CaveOfSummons1F")

                graph[location][type].append(destination)
        paths_to_world = {}
        is_loop=False
        locations_to_ignore = ["#SylvanCaveTreasury"]
        for location in graph:
            if location in locations_to_ignore:
                continue
            paths_to_world[location]=[]
            for world in ["#Overworld", "#Underworld", "#Moon"]:
                paths_to_world[location] += find_all_paths(graph, world,location , "entrances",[])
            if paths_to_world[location]:
                is_loop = True
                continue
            else:
                print("not able find overworld to exit for:", location, "due to loop... retrying")
                is_loop = False
                break
        if is_loop:
            break
        print("not able to validate exits, retrying")
    print("needed loops: ", loop_count, "to validate exits for ")

    for i in paths_to_world:
        print(i,paths_to_world[i])

    return2teleport = ["mapgrid ($04 17 31) { 7C }",  # Silvera return tile to trigger tile
                       "mapgrid ($05 16 29) { 7C }",  # Tororia return tile to trigger tile
                       "mapgrid ($06 15 31) { 7C }",  # Agart return tile to trigger tile
                       "mapgrid ($06 16 31) { 7C }",  # Agart return tile to trigger tile
                       "mapgrid ($06 17 31) { 7C }",  # Agart return tile to trigger tile
                       "mapgrid ($136 17 9) { 72 }",  # CaveOfSummons1F return tile to trigger tile
                       "mapgrid ($13A 12 14) { 25 }",  # Feymarch 1F return tile to trigger tile
                       "mapgrid ($13B 16 21) { 25 }",  # Feymarch treasury return tile to trigger tile
                       "mapgrid ($13B 16 24) { 51 }",  # Feymarch treasury removing exit tile
                       "mapgrid ($13C 28 11) { 25 }",  # Feymarch 2F return tile to trigger tile
                       "mapgrid ($145 16 1) { 72 }",  # Sylph Cave return tile to trigger tile
                       "mapgrid ($149 11 10) { 70 }",  # Sylph Yang Room removing exit tile
                       "mapgrid ($149 9 4) { 23 }",  # Sylph Yang room return tile to trigger tile
                       ]
    remapped_ = []
    remapped_spoiled = []
    special_triggers = []
    remapped_ += shuffled_entrances + shuffled_exits
    remapped_spoiled += spoil_entrances
    print("len of remapped=", len(remapped_))
    script = ""

    for index, i in enumerate(remapped_):
        # Ok, so this is a big ugly hack to stick a lookup index into the trigger data
        # without breaking the compilation process.
        # We use a special map id to indicate that the trigger should be overridden.
        # (we TRIED using the apparently unused "#CurrentMap" ($FE), but it turns out $FE
        #  has a special meaning for the compiler, indicating a treasure trigger)
        # Because we're relying on the compiler, we only get 6 bits for the target's X
        # coord, so we put the high byte in there and the low byte in the target's Y coord.
        # In the long run, we'd probably want to manually override the trigger data,
        # rather than hacking around the f4c compiler.
        script += (
            f'trigger({i[0]} {i[1]}) {{\n'
            f'position {i[2]} {i[3]}\n'
            f'teleport #EndingFabulThroneRoom at {index >> 8} {index & 0xFF}'
        )

        x_coord = i[6]
        if i[5] not in ["#Overworld", "#Underworld", "#Moon"]:
            x_coord |= (DIRECTION_MAP[i[8]] << 6)
        script += f'  // [${index:04X}] {i[5]} at {i[6]} {i[7]}\n'
        script += f'facing up'
        script += '}\n\n'
        special_triggers.append(f"##map.{i[5][1:]} {x_coord:X} {i[7]:X}")
        # print(script)
        # random assignment just for testing:
        # map_id = env.rnd.randint(0, 0x17E)
        # special_triggers.append(f"{map_id & 0xFF:02X} {map_id >> 8:02X} 90 10")

    bytes_used = len(special_triggers) * 4
    if not testing:

        key_items = {str(env.assignments[x]): ki_location[str(x)] for x in env.assignments if
                     "*" in str(env.assignments[x])}
        print(key_items)
        magma_location = key_items['*[#item.Magma]']
        hook_location = key_items['*[#item.fe_Hook]']
        print("Magma",magma_location,paths_to_world[magma_location])

        # for i in env.assignments:
        #     name = str(i)
        #     if "*" in str(env.assignments[i]) and "fixed_crystal" not in name:
        #
        #         if Magma
        #
        #         print(name, str(env.assignments[i]), ki_location[name])

        for i in return2teleport:
            env.add_script(i)

        env.add_script(script)
        special_triggers_script = '\n'.join(special_triggers)
        env.add_script(f'patch(${rom_base.get_bus():06X} bus) {{\n{special_triggers_script}\n}}')
    # print(script)

    towns_map = []
    other_entrances = []
    for i in sorted(remapped_spoiled):
        istown = ""
        for j in towns_flat:
            if i.startswith(j + " is in"):
                istown = True
                break
        if istown:
            towns_map.append(i)
        else:
            other_entrances.append(i)

    print("\n".join(["", "", "", ] + towns_map + ["", "", "", ] + other_entrances))

    #

    return bytes_used


if __name__ == '__main__':
    import random
    class Environment:
        def __init__(self):
            self.rnd = random.Random()
    apply(Environment(), None, True)
