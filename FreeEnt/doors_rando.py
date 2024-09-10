import json

try:
    from . import databases
except ImportError:
    import databases

towns = {"#Overworld": ['#BaronTown', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart'],
         "#Underworld": ['#Tomra', '#Feymarch1F', "#Feymarch2F", "#CaveOfSummons1F", "#SylvanCave1F"], "#Moon": []}
towns_flat = ['#BaronTown', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart', '#Tomra',
              '#Feymarch1F', "#Feymarch2F", "#CaveOfSummons1F", "#SylvanCave1F"]

ki_lock = {"*[#item.Baron]": ["#RoomToSewer", "RewardSlot.baron_castle_item", "RewardSlot.baron_throne_item"],
           "*[#item.DarkCrystal]": ["#Moon", "RewardSlot.giant_chest"],
           "*[#item.EarthCrystal]": ["RewardSlot.zot_chest"],
           "*[#item.fe_Hook]": ["#Underworld", "#CaveEblanEntrance", "#AdamantGrotto", "RewardSlot.pink_trade_item"],
           "*[#item.Luca]": ["RewardSlot.sealed_cave_item"], "*[#item.Magma]": ["#Underground"],
           "*[#item.Pan]": ["RewardSlot.pan_trade_item", "RewardSlot.sylph_item"],
           "*[#item.Pink]": ["RewardSlot.pink_trade_item"], "*[#item.Rat]": ["RewardSlot.rat_trade_item"],
           "*[#item.Tower]": ["RewardSlot.cannon_item"], "*[#item.TwinHarp]": ["RewardSlot.magnes_item"]}

entrances_locked = {"#RoomToSewer": "*[#item.Baron]", "#Moon": "*[#item.DarkCrystal]",
                    "#Underworld": "*[#item.Magma]|*[#item.fe_Hook]", "#CaveEblanEntrance": "*[#item.fe_Hook]",
                    "#AdamantGrotto": "*[#item.fe_Hook]"}

slots_locked = {"RewardSlot.baron_castle_item": "*[#item.Baron]", "RewardSlot.baron_throne_item": "*[#item.Baron]",
                "RewardSlot.giant_chest": "*[#item.DarkCrystal]", "RewardSlot.zot_item": "*[#item.EarthCrystal]",
                "RewardSlot.pink_trade_item": "*[#item.Pink]", "RewardSlot.sealed_cave_item": "*[#item.Luca]",
                "RewardSlot.pan_trade_item": "*[#item.Pan]", "RewardSlot.sylph_item": "*[#item.Pan]",
                "RewardSlot.rat_trade_item": "*[#item.Rat]", "RewardSlot.cannon_item": "*[#item.Tower]",
                "RewardSlot.magnes_item": "*[#item.TwinHarp]"}

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
               "RewardSlot.starting_character": "None", "RewardSlot.starting_item": "starting",
               "RewardSlot.starting_partner_character": "None", "RewardSlot.sylph_cave_chest_1": "#SylvanCave1F",
               "RewardSlot.sylph_cave_chest_2": "#SylvanCave1F", "RewardSlot.sylph_cave_chest_3": "#SylvanCave1F",
               "RewardSlot.sylph_cave_chest_4": "#SylvanCave1F", "RewardSlot.sylph_cave_chest_5": "#SylvanCave1F",
               "RewardSlot.sylph_cave_chest_6": "#SylvanCave1F", "RewardSlot.sylph_cave_chest_7": "#SylvanCave1F",
               "RewardSlot.sylph_item": "#SylvanCaveYangRoom", "RewardSlot.upper_babil_chest": "#ToroiaCastle",
               "RewardSlot.watery_pass_character": "#WateryPass1F|#WateryPass5F",
               "RewardSlot.zot_character_1": "#ToroiaCastle", "RewardSlot.zot_character_2": "#ToroiaCastle",
               "RewardSlot.zot_chest": "#ToroiaCastle", "RewardSlot.zot_item": "#ToroiaCastle",
               "RewardSlot.fixed_crystal": "#LunarPalaceLobby"}
slot_locations = {"dmist_slot": "#MistCave", "officer_slot": "#Mist&#Kaipo", "octomamm_slot": "#Waterfall2F",
                  "antlion_slot": "#AntlionCave1F", "mombomb_slot": "#MountHobsEast", "fabulgauntlet_slot": "#Fabul",
                  "milon_slot": "#MountOrdeals1F", "milonz_slot": "#MountOrdeals1F",
                  "mirrorcecil_slot": "#MountOrdeals1F", "karate_slot": "#BaronInn", "guard_slot": "#BaronInn",
                  "baigan_slot": "#RoomToSewer", "kainazzo_slot": "#RoomToSewer", "darkelf_slot": "#CaveMagnes1F",
                  "magus_slot": "#ToroiaCastle", "valvalis_slot": "#ToroiaCastle",
                  "calbrena_slot": "#DwarfCastle|#DwarfCastleBasement",
                  "golbez_slot": "#DwarfCastle|#DwarfCastleBasement", "lugae_slot": "#Babil1F",
                  "darkimp_slot": "#Babil1F", "kingqueen_slot": "#CaveEblanEntrance",
                  "rubicant_slot": "#CaveEblanEntrance", "evilwall_slot": "#SealedCaveEntrance",
                  "asura_slot": "#FeymarchLibrary1F", "leviatan_slot": "#FeymarchLibrary1F",
                  "odin_slot": "#RoomToSewer", "bahamut_slot": "#Bahamut1F", "elements_slot": "None",
                  "cpu_slot": "None", "paledim_slot": "#LunarPalaceLobby}", "wyvern_slot": "#LunarPalaceLobby",
                  "plague_slot": "#LunarPalaceLobby", "dlunar_slot": "#LunarPalaceLobby",
                  "ogopogo_slot": "#LunarPalaceLobby"}
DIRECTION_MAP = {
    'up': 0,
    'right': 1,
    'down': 2,
    'left': 3,
}


def map_exit_to_entrance(remapped_entrances, exit):
    if "SylvanCaveTreasury" in exit[0] or "#SylvanCave3F" in exit[0]:
        exit = ["#SylvanCave1F", "", "", "", "#Underworld"]
    elif "CaveOfSummons3F" in exit[0]:
        exit = ["#CaveOfSummons1F", "", "", "", "#Underworld"]
    elif exit[0] == "#EblanBasement":
        exit = ["#Eblan", "", "", "", "#Overworld"]

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
    towns_ = towns_flat
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
        if entrance:
            remapped_exits.append(i[0:4] + [i[-2]] + entrance)
        else:
            print("not found")
            print(i)
    return [remapped_entrances, remapped_exits]


def sync_entrances_exits(graph):
    new_graph = graph.copy()
    for location in graph:
        entrances = graph[location]["entrances"]
        exits = graph[location]["exits"]

        for entrance in entrances:
            if entrance not in new_graph:
                new_graph[entrance] = {"entrances": [], "exits": []}
            if location not in new_graph[entrance]["exits"]:
                new_graph[entrance]["exits"].append(location)
        for exit_ in exits:
            if exit_ not in new_graph:
                new_graph[exit_] = {"entrances": [], "exits": []}
            if location not in new_graph[exit_]["entrances"]:
                new_graph[exit_]["entrances"].append(location)

    return new_graph


def find_all_paths(graph, start, end, type, path=[]):
    path = path + [start]
    if start == end:
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


def map_path_to_entrance_names(path, remapped_map):
    new_path = []
    for location in path:
        if location in ["#Overworld", "#Underworld", "#Moon"]:
            new_path.append(location)
        else:
            try:
                new_path.append([remapped_map[location], location])
            except KeyError:
                new_path.append([location, location])
    return new_path


def randomize_doors(env, entrances, exits):
    is_loop = False
    loop_count = 0
    tries = 1
    paths_to_world = {}
    graph = {}
    remapped_map = {}
    shuffled_entrances = {}
    shuffled_exits = {}
    spoil_entrances = []
    while not is_loop:
        graph = {}
        remapped_map = {}
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
                    if j[5] == "#Mist":
                        if "#Mist" not in remapped_map:
                            remapped_map[j[5]] = []
                        remapped_map[j[5]].append(j[4].split('_')[1])

                    else:
                        remapped_map[j[5]] = j[4].split('_')[1]
                    spoil_entrances.append(message)
            else:
                type = "exits"
            if location not in graph:
                graph[location] = {"entrances": [], "exits": []}
            if destination not in graph[location][type]:
                graph[location][type].append(destination)

        paths_to_world = {}
        is_loop = False

        try:
            graph["#SylvanCave1F"]["entrances"].append("#SylvanCave3F")
            graph["#CaveOfSummons1F"]["entrances"].append("#CaveOfSummons3F")
            graph["#SylvanCave3F"]["exits"].append("#SylvanCave1F")
            graph["#CaveOfSummons3F"]["exits"].append("#CaveOfSummons1F")
        except:
            pass  # Not underworld
        graph = sync_entrances_exits(graph)

        locations_to_ignore = ["#SylvanCaveTreasury", "#EblanBasement", "#CaveOfSummons3F", "#SylvanCave3F"]
        for location in graph:
            if location in locations_to_ignore:
                continue
            paths_to_world[location] = []
            for world in ["#Overworld", "#Underworld", "#Moon"]:
                paths_to_world[location] += find_all_paths(graph, world, location, "entrances", [])
            if paths_to_world[location]:
                location_doors = []
                for path in paths_to_world[location]:
                    location_doors.append(map_path_to_entrance_names(path, remapped_map))
                paths_to_world[location] = location_doors
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
    return shuffled_entrances, shuffled_exits, spoil_entrances, graph, paths_to_world


def get_entrances_exits(world_object, doors_view):
    entrances = []
    exits = []
    if isinstance(world_object, list):
        for world in world_object:
            entrances += [list(i) for i in doors_view.find_all(
                lambda sp: (sp.type == "entrance" or sp.type == "town_building") and sp.world == world)]
            exits += [list(i) for i in
                      doors_view.find_all(lambda sp: (sp.type == "exit" or sp.type == "return") and sp.world == world)]
    else:
        entrances += [list(i) for i in doors_view.find_all(
            lambda sp: (sp.type == "entrance" or sp.type == "town_building") and sp.world == world_object)]
        exits += [list(i) for i in
                  doors_view.find_all(
                      lambda sp: (sp.type == "exit" or sp.type == "return") and sp.world == world_object)]

    return entrances, exits

def return_gated_paths(paths_to_world):
    gated_paths = {}
    for path in paths_to_world:

        gated_by = []
        for entrance in paths_to_world[path]:
            if isinstance(entrance, str):
                entrance_name = entrance

            else:
                entrance_name = entrance[0]
            if not isinstance(entrance_name, str):
                entrance_name_1, entrance_name_2 = entrance_name
                locked_1 = ""
                locked_2 = ""
                try:
                    locked_1 = entrances_locked[entrance_name_1]
                except KeyError:
                    pass  # not gated
                try:
                    locked_2 = entrances_locked[entrance_name_2]
                except KeyError:
                    pass  # not gated

                if locked_1 and locked_2:
                    gated_by.append(locked_1 + "|" + locked_2)

            else:
                try:

                    gated_by.append(entrances_locked[entrance_name])
                except KeyError:
                    pass  # not gated
        gated_paths[path] = gated_by
    return gated_paths


def return_gated_kis(key_items, gated_paths):
    gated_ki = {}
    for i in key_items:
        gated_ki[i] = {}
        gated_ki[i]["and"] = []
        gated_ki[i]["or"] = []
        ki_required_location=""
        try:
            ki_required_location = key_items[i]["and_location"]
        except:
            pass
        if ki_required_location:
            if ki_required_location:
                for location in ki_required_location:
                    gated_ki[i]["and"] += gated_paths[location]
                if len(gated_ki[i]["and"]) ==2 and gated_ki[i]["and"][0] == gated_ki[i]["and"][1]:
                        gated_ki[i]["and"] = gated_ki[i]["and"][0]
                if len(gated_ki[i]["and"]) ==1 and gated_ki[i]["and"][0] == "*[#item.Magma]|*[#item.fe_Hook]":
                    gated_ki[i]["and"]=[]
                    gated_ki[i]["or"] = [["*[#item.Magma]"],["*[#item.fe_Hook]"]]
                elif len(gated_ki[i]["and"]) == 2:

                    if gated_ki[i]["and"][0] == "*[#item.Magma]|*[#item.fe_Hook]":
                        gated_ki[i]["or"] += ["*[#item.Magma]", "*[#item.fe_Hook]"]
                        gated_ki[i]["and"] = gated_ki[i]["and"][1]
                    elif gated_ki[i]["and"][1] == "*[#item.Magma]|*[#item.fe_Hook]":
                        gated_ki[i]["or"] += [["*[#item.Magma]"], ["*[#item.fe_Hook]"]]
                        gated_ki[i]["and"] = gated_ki[i]["and"][0]

        else:
            try:
                ki_required_location = key_items[i]["or_location"]
            except:
                continue
            if ki_required_location:
                for location in ki_required_location:
                    gated_ki[i]["or"] += gated_paths[location]
                if len(gated_ki[i]["or"])<2:
                    gated_ki[i]["or"]=[]

                elif gated_ki[i]["or"][0] == gated_ki[i]["or"][1]:
                    if gated_ki[i]["or"][0] == "*[#item.Magma]|*[#item.fe_Hook]":
                        gated_ki[i]["or"] = [["*[#item.Magma]"], ["*[#item.fe_Hook]"]]
                    else:
                        gated_ki[i]["and"] = [gated_ki[i]["or"][0]]
                    gated_ki[i]["or"]=[]


    return gated_ki


def return_gated_slots(key_items, gated_ki):
    gated_slots = {}
    for i in key_items:
        gated_slots[i] = {}

        slot_location = key_items[i]["slot"]
        try:
            ki_required_for_slot = slots_locked[slot_location]
            gated_slots[i]["and"] = [ki_required_for_slot]
            try:
                gated_slots[i]["and"] += gated_ki[ki_required_for_slot]["and"]
            except KeyError:
                pass
        except:
            pass
        if not gated_slots[i]:
            del gated_slots[i]
    return gated_slots

# def return_all_recursive_required_ki(key_item,ki_full_locked,ki_required=[]):
#     ki_required

def recursive_spheres(available_ki,locked_stack,ki_full_locked,spheres,current_sphere):
    locked_temp=[]
    available_temp = []
    spheres[current_sphere]=[]
    temp_array=[]
    for i in locked_stack:
        if isinstance(i,list):
            i=i[0]
        temp_array.append(i)

    locked_stack=list(temp_array)
    for i in locked_stack:

        if isinstance(i,list):
            i=i[0]
        ands=ki_full_locked[i]["and"]
        ors=ki_full_locked[i]["or"]
        is_available=True
        if ands:
            temp_array = []
            for j in ands:
                if isinstance(j, list):
                    j = j[0]
                temp_array.append(j)

            ands = list(temp_array)

            for ki in ands:
                if ki not in available_ki:
                    is_available=False
                    break

        if ors:
            temp_array = []
            for j in ors:
                if isinstance(j, list) and len(j)==1:
                    j = j[0]
                temp_array.append(j)
            ors = list(temp_array)
            all_available_parent=[]
            for or_path in ors:
                if isinstance(or_path,list):
                    all_available_sub=[]
                    for ki in or_path:
                        if isinstance(ki, list) and len(ki) == 1:
                            ki = ki[0]

                        if ki not in available_ki:
                            all_available_sub.append(False)
                    if False in all_available_sub:
                        all_available_parent.append(False)
                    else:
                        all_available_parent.append(True)


                else:
                    if or_path not in available_ki:
                        all_available_parent.append(False)
                    else:
                        all_available_parent.append(True)

            if True not in all_available_parent:
                is_available=False
            else:
                is_available=True
        if is_available:
            spheres[current_sphere].append(i)
            available_temp.append(i)
        else:
            if i not in locked_temp:
                locked_temp.append(i)
    if sorted(locked_temp)==sorted(locked_stack):
        return False
    elif locked_temp:
        current_sphere+=1
        available_ki+=available_temp
        return recursive_spheres(available_ki,locked_temp,ki_full_locked,spheres,current_sphere)
    elif not locked_temp:
        return spheres


def calculate_spheres(ki_full_locked):
    spheres={}
    current_sphere=0
    spheres[current_sphere]=[]
    available_ki=[]
    locked_stack=[]
    for i in ki_full_locked:
        if not ki_full_locked[i]["and"] and not ki_full_locked[i]["or"]:
            spheres[current_sphere].append(i)
        else:
            locked_stack.append(i)
    available_ki += spheres[current_sphere]
    current_sphere+=1
    is_valid = recursive_spheres(available_ki,locked_stack,ki_full_locked,spheres,current_sphere)
    return is_valid
def normalize_ands_ors(ki_full_locked):
    for i in ki_full_locked:
        ands = ki_full_locked[i]["and"]
        ors = ki_full_locked[i]["or"]
        if ands and ors:
            new_ors = []
            for or_ki in ors:
                new_ors.append(ands+[or_ki])
            ki_full_locked[i]["and"]=[]
            ki_full_locked[i]["or"]=new_ors

    return ki_full_locked

def check_logic(key_items, paths_to_world):
    gated_paths = return_gated_paths(paths_to_world)
    gated_ki = return_gated_kis(key_items, gated_paths)
    gated_slots = return_gated_slots(key_items, gated_ki)

    ki_full_locked = {}
    for i in key_items:
        ki_full_locked[i] = {"and":[],"or":[]}
        if i in gated_ki:
            try:
                ki_full_locked[i]["and"] += gated_ki[i]["and"]
            except:
                pass
            try:
                ki_full_locked[i]["or"] += gated_ki[i]["or"]
            except:
                pass

        if i in gated_slots:
            ki_full_locked[i]["and"] += gated_slots[i]["and"]

    ki_full_locked = normalize_ands_ors(ki_full_locked)
    # for i in ki_full_locked:
    #     print(i,ki_full_locked[i])
    return calculate_spheres(ki_full_locked)

def apply(env, rom_base, randomize_type,testing=False):
    doors_view = databases.get_doors_dbview()
    print(f"Rando type is {randomize_type}")
    # randomize_type = "gated"
    if randomize_type == "normal":
        worlds = ["#Overworld", "#Underworld", "#Moon"]
    elif randomize_type == "blue_planet":
        worlds = [["#Overworld", "#Underworld"], "#Moon"]
    elif randomize_type == "gated":
        worlds = ["#Overworld", ["#Underworld", "#Moon"]]
    elif randomize_type == "why":
        worlds = [["#Overworld", "#Moon"], "#Underworld"]
    elif randomize_type == "all":
        worlds = [["#Overworld", "#Underworld", "#Moon"]]
    else:
        worlds = ["#Overworld", "#Underworld", "#Moon"]
    attempts=0
    while attempts < 20:
        shuffled_entrances = []
        shuffled_exits = []
        spoil_entrances = []
        graph = {}
        paths_to_world = {}
        for i in worlds:
            entrances, exits = get_entrances_exits(i, doors_view)
            shuffled_entrances_temp, shuffled_exits_temp, spoil_entrances_temp, graph_temp, paths_to_world_temp = randomize_doors(
                env, entrances, exits)
            shuffled_entrances += shuffled_entrances_temp
            shuffled_exits += shuffled_exits_temp
            spoil_entrances += spoil_entrances_temp
            graph.update(graph_temp)
            paths_to_world.update(paths_to_world_temp)
        print(env.assignments)
        for i in env.assignments:
            print(str(i),str(env.assignments[x]))
        key_items = {str(env.assignments[x]): {"location": ki_location[str(x)], "slot": str(x)} for x in env.assignments
        if
                     "*" in str(env.assignments[x]) and "[#item.Crystal]" not in str(env.assignments[x])}

        dmist_slot = [str(x) for x in env.assignments if str(env.assignments[x]) == "dmist"][0]

        for item in key_items:
            ki_required_room = key_items[item]["location"]
            if ki_required_room == "starting":
                key_items[item]["and"] = None
                key_items[item]["and_location"] = None
                continue

            if '|' in ki_required_room:
                key_items[item]["or"] = []

                ki_required_room = ki_required_room.split("|")
                key_items[item]["or_location"] = ki_required_room
                for room in ki_required_room:
                    key_items[item]["or"] += paths_to_world[room]

            elif '&' in ki_required_room:
                key_items[item]["and"] = []

                ki_required_room = ki_required_room.split("&")
                key_items[item]["and_location"] = ki_required_room
                for room in ki_required_room:
                    key_items[item]["and"] += (paths_to_world[room])

            else:
                key_items[item]["and"] = paths_to_world[ki_required_room]
                key_items[item]["and_location"] = [ki_required_room]
        is_valid = check_logic(key_items, paths_to_world)
        if not is_valid:
            attempts+=1
        else:
            print(f"Needed {attempts+1} attempts for KI to be available")
            print(is_valid)
            break

    # for i in paths_to_world:
    #     print(i, paths_to_world[i])

    remapped_ = []
    remapped_spoiled = []
    special_triggers = []
    remapped_ += shuffled_entrances + shuffled_exits
    remapped_spoiled += spoil_entrances
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

    bytes_used = len(special_triggers) * 4
    key_items = {str(env.assignments[x]): {"location": ki_location[str(x)], "slot": str(x)} for x in env.assignments
                 if
                 "*" in str(env.assignments[x]) and "[#item.Crystal]" not in str(env.assignments[x])}

    dmist_slot = [str(x) for x in env.assignments if str(env.assignments[x]) == "dmist"][0]

    for item in key_items:
        ki_required_room = key_items[item]["location"]
        if ki_required_room == "starting":
            key_items[item]["and"] = None
            key_items[item]["and_location"] = None
            continue

        if '|' in ki_required_room:
            key_items[item]["or"] = []

            ki_required_room = ki_required_room.split("|")
            key_items[item]["or_location"] = ki_required_room
            for room in ki_required_room:
                key_items[item]["or"] += paths_to_world[room]

        elif '&' in ki_required_room:
            key_items[item]["and"] = []

            ki_required_room = ki_required_room.split("&")
            key_items[item]["and_location"] = ki_required_room
            for room in ki_required_room:
                key_items[item]["and"] += (paths_to_world[room])

        else:
            key_items[item]["and"] = paths_to_world[ki_required_room]
            key_items[item]["and_location"] = [ki_required_room]
    check_logic(key_items, paths_to_world)

        # for item in key_items:
        #     print(item, key_items[item])

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
                       "mapgrid ($160 16 29) { 6E }",  # Lunar Palace Lobby return tile to trigger tile
                       ]
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

    print ("\n".join(["", "", "", ] + towns_map + ["", "", "", ] + other_entrances))

    return bytes_used


if __name__ == '__main__':
    import random


    class Environment:
        def __init__(self):
            self.rnd = random.Random()


    apply(Environment(), None, True)
