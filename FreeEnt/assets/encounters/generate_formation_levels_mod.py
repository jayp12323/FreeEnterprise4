import f4c
import os

rom = f4c.ff4bin.Rom('PATH-TO-ROM')

# The way the vanilla game checks for average level is to take the average level
# of *every* monster in the battle, even the ones that are hidden at the start.
# That means we will also include monsters that get "called", e.g. D.Machin.
# "Transforming" monsters don't really matter because they only appear in boss bit
# formations, which we'll still set as 0, so include them as well.
# These changes, together with a bugfix for the vanilla code to check all of
# the monster slots inside of just the first three and a bugfix for the average
# party level computation that Edanger does, mean that Evanilla and Edanger will 
# act the same when it comes to surprise/back attacks.

results = []
for formation_index in range(0x200):
    formation = f4c.ff4struct.formation.decode(rom.formations[formation_index])

    relevant_indices = [0, 1, 2]
    # no removal of indices; consider all three monster types!

    enemy_levels = []
    has_boss = False
    for i in relevant_indices:
        if formation.monster_qtys[i]:
            monster_id = formation.monster_types[i]
            monster = f4c.ff4struct.monster.decode(rom.monsters[monster_id])
            enemy_levels.extend([monster.level] * formation.monster_qtys[i])
            if monster.boss:
                has_boss = True

    if (not enemy_levels) or has_boss:
        results.append(0)
    else:
        avg_enemy_level = sum(enemy_levels) // len(enemy_levels)
        results.append(avg_enemy_level)

    if (has_boss):
        print(f'Formation {formation_index:03X} - is boss')

with open('formation_average_levels_mod.bin', 'wb') as outfile:
    outfile.write(bytes(results))
