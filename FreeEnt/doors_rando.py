import json
import re
import sys

try:
    from . import databases
except ImportError:
    import databases
import random

rnd = random.Random()
towns = {"#Overworld": ['#BaronTown', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart'],
         "#Underworld": ['#Tomra', "#Feymarch2F", "#CaveOfSummons1F"], "#Moon": []}
towns_flat=['#BaronTown', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart','#Tomra', "#CaveOfSummons1F"]

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


def shuffle_locations(entrances, exits, world):
    max_towns_in_overworld={"#Overworld": 4, "#Underworld": 2, "#Moon": 10}
    towns_ = towns[world]
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
    max_towns_in_overworld = random.randint(1, max_towns_in_overworld[world])
    overworld_entrances = 0
    print("max_towns", world, max_towns_in_overworld)
    tries = 0
    while exit__:
        if tries > 20:
            return False
        exit___ = exit__.pop(0)
        shuffled_exit = shuffled_exits.pop(0)
        if shuffled_exit[0] in towns_ and shuffled_exit[4] == 'entrance' and exit___[4] == "entrance":
            overworld_entrances += 1
        if ((shuffled_exit[0] in towns_ and shuffled_exit[4] == 'entrance' and exit___[5].split("_")[0] ==
             shuffled_exit[0])
                or (shuffled_exit[0] == "#CaveOfSummons1F" and shuffled_exit[4] == 'entrance' and exit___[5].split("_")[
                    0] == "#Feymarch2F")
                or (overworld_entrances > max_towns_in_overworld)):
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
            if "SylvanCave" in i[0]:
                entrance = map_exit_to_entrance(remapped_entrances, ["#SylvanCave1F", "", "", "", "#Underworld"])

            elif i[0] == "#EblanBasement":
                entrance = map_exit_to_entrance(remapped_entrances, ["#Eblan", "", "", "", "#Overworld"])

            elif i[0] == "#FeymarchTreasury":
                entrance = map_exit_to_entrance(remapped_entrances, ["#CaveOfSummons1F", "", "", "", "#Underworld"])

        if entrance:
            remapped_exits.append(i[0:4] + [i[-2]] + entrance)
        else:
            print("not found")
            print(i)


    return [remapped_entrances, remapped_exits]


def has_exit(graph, town, towns_with_exit, checked=[], stack=[]):
    print(town, stack, checked)
    if town not in checked:
        checked.append(town)
    if [element for element in checked if element in towns_with_exit]:
        return True
    else:
        stack += graph[town]["exits"]
        town = stack.pop(0)
        return has_exit(graph, town, towns_with_exit, checked, stack)

def apply(env, testing=False):
    doors_view = databases.get_doors_dbview()

    num_dupes=0
    no_dupes=False
    while not no_dupes:
        shuffled_entrances = []
        shuffled_exits = []
        spoil_entrances = []

        for i in ["#Overworld", "#Underworld", "#Moon"]:
            graph = {}
            entrances = [list(i) for i in doors_view.find_all(
                lambda sp: (sp.type == "entrance" or sp.type == "town_building") and sp.world == i)]
            exits = [list(i) for i in
                     doors_view.find_all(lambda sp: (sp.type == "exit" or sp.type == "return") and sp.world == i)]

            is_loop = False
            loop_count = 0
            tries = 1
            while not is_loop:
                if loop_count > 200:
                    raise ChildProcessError
                loop_count += 1
                max_tries = 100
                try:
                    remapped_entrances, remapped_exits = shuffle_locations(entrances, exits, i)
                except TypeError:
                    tries += 1
                    if tries < max_tries:
                        continue
                    else:
                        return False
                print("max locations took tries: ",tries, "for world ", i)
                shuffled_entrances += remapped_entrances
                shuffled_exits += remapped_exits

                for j in remapped_entrances + remapped_exits:
                    location = j[0]
                    destination = j[5]
                    if len(j) == 13:
                        type = "entrances"
                        if f"{j[4].split('_')[1]} leads to {j[5]}" not in spoil_entrances:
                            spoil_entrances.append(f"{j[4].split('_')[1]} leads to {j[5]}")
                    else:
                        type = "exits"
                    if location not in graph:
                        graph[location] = {"entrances": [], "exits": []}
                    if destination not in graph[location][type]:
                        graph[location][type].append(destination)
                if i == "#Underworld":
                    graph["#Feymarch2F"]["exits"] = graph["#CaveOfSummons1F"]["exits"]

                elif i=="#Moon":
                    break

                towns_with_exit = [town for town in towns[i] if i in graph[town]["exits"]]
                print(towns_with_exit)
                if not towns_with_exit:
                    print("No exits found, trying again")
                    continue
                sys.setrecursionlimit(50)
                try:
                    for town in towns[i]:
                        print("for town", town)
                        if has_exit(graph, town, towns_with_exit, [], []):

                            is_loop = True
                            continue
                        else:
                            print("not able to exit for: ", town, ", retrying")
                            raise RecursionError
                except RecursionError:
                    pass
                if is_loop:
                    break
                print("not able to validate exits, retrying")
            print("needed loops: ", loop_count, "to validate exits for ",i)
        sys.setrecursionlimit(1000)
        return2teleport = ["mapgrid ($04 17 31) { 7C }",
                           "mapgrid ($05 16 29) { 7C }",
                           "mapgrid ($06 15 31) { 7C }",
                           "mapgrid ($06 16 31) { 7C }",
                           "mapgrid ($136 17 9) { 74 }", ]

        remapped_ = shuffled_entrances + shuffled_exits
        if len(remapped_)==171:
            no_dupes=True
        else:
            num_dupes+=1

    print("needed tries to not get dupes",num_dupes)
    script=""
    for i in remapped_:
        script += '''trigger({0} {1})
    {{
        position {2} {3}
        teleport {5} at {6} {7}'''.format(*i)

        if i[5] not in ["#Overworld", "#Underworld", "#Moon"]:
            script += " facing {8}".format(*i)
        script += '''
    }
    
    '''
    if not testing:
        for i in return2teleport:
            env.add_script(i)

        env.add_script(script)
    # print(script)

    towns_map=[]
    other_entrances=[]
    for i in sorted(spoil_entrances):
        istown=""
        for j in towns_flat:
            if i.endswith(j):
                istown=True
                break
        if istown:
            towns_map.append(i)
        else:
            other_entrances.append(i)

    print ("\n".join(towns_map+other_entrances))
if __name__ == '__main__':
    apply(None, True)
