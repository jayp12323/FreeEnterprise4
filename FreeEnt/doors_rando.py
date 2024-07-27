try:
    from . import databases
except ImportError:
    import databases
import random

rnd = random.Random()


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


def shuffle_locations(env, entrances, exits, testing=False):
    entrance_destinations = [entrance[4:] for entrance in entrances]
    exit_dict = {}
    for dest in entrance_destinations:
        exit_tup = (dest[0], dest[3])
        if exit_tup not in exit_dict:
            exit_dict[exit_tup] = dest[1:]

    exit__ = [[list(i)[0]] + exit_dict[i] + [list(i)[1]] for i in exit_dict]
    shuffled_exits = list(exit__)
    exit_dict = {}
    rnd.shuffle(shuffled_exits)
    towns = ['#BaronTown', '#Mist', '#Kaipo', '#Mysidia', '#Silvera', '#ToroiaTown', '#Agart', '#Tomra']
    while exit__:
        exit___ = exit__.pop(0)
        shuffled_exit = shuffled_exits.pop(0)
        if shuffled_exit[0] in towns and shuffled_exit[4] == 'entrance' and exit___[4] == 'town_building':
            exit__ = [exit___] + exit__
            shuffled_exits.append(shuffled_exit)
            continue
        exit_dict[tuple([exit___[0], exit___[3]])] = shuffled_exit
    remapped_entrances = []
    for entrance in entrances:
        exit = tuple([entrance[4], entrance[7]])
        remapped_exit = exit_dict[exit]
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

    remapped_ = remapped_entrances + remapped_exits

    grids = ["mapgrid ($04 17 31) { 7C }",
             "mapgrid ($05 16 29) { 7C }",
             "mapgrid ($06 15 31) { 7C }",
             "mapgrid ($06 16 31) { 7C }",
             "mapgrid ($06 17 31) { 7C }", ]


    for i in remapped_:
        script = '''trigger({0} {1})
    {{
        position {2} {3}
        teleport {5} at {6} {7}'''.format(*i)

        if i[5] not in ["#Overworld", "#Underworld", "#Moon"]:
            script += " facing {8}".format(*i)
        script += '''
    }
    '''
        print(i)
        if not testing:
            for i in grids:
                env.add_script(i)

            env.add_script(script)
            print(script)


def apply(env, testing=False):
    doors_view = databases.get_doors_dbview()

    for i in ["#Overworld", "#Underworld", "#Moon"]:
        entrances = [list(i) for i in doors_view.find_all(
            lambda sp: ((sp.type == "entrance" or sp.type == "town_building")) and sp.world == i)]
        exits = [list(i) for i in
                 doors_view.find_all(lambda sp: ((sp.type == "exit" or sp.type == "return")) and sp.world == i)]

        shuffle_locations(env, entrances, exits, testing)


if __name__ == '__main__':
    apply(None, True)
