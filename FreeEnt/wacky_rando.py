import os

from . import databases
from . import doors_rando

from .address import *
from .core_rando import BOSS_SLOTS

WACKY_CHALLENGES = {
    'musical'           : 'Final Fantasy IV:\nThe Musical',
    'bodyguard'         : 'The Bodyguard',
    'fistfight'         : 'Fist Fight',
    'omnidextrous'      : 'Omnidextrous',
    'biggermagnet'      : 'A Much\nBigger Magnet',
    'sixleggedrace'     : 'Six-Legged Race',
    'floorislava'       : 'The Floor Is\nMade Of Lava',
    'neatfreak'         : 'Neat Freak',
    'timeismoney'       : 'Time is Money',
    'nightmode'         : 'Night Mode',
    'mysteryjuice'      : 'Mystery Juice',
    'misspelled'        : 'Misspelled',
    'enemyunknown'      : 'Enemy Unknown',
    'kleptomania'       : 'Kleptomania',
    'darts'             : 'World Championship\nof Darts',
    'unstackable'       : 'Unstackable',
    'menarepigs'        : 'Men Are Pigs',
    'skywarriors'       : 'The Sky Warriors',
    'zombies'           : 'Zombies!!!',
    'afflicted'         : 'Afflicted',
    'batman'            : 'Holy Onomatopoeias,\nBatman!',
    'battlescars'       : 'Battle Scars',
    'imaginarynumbers'  : 'Imaginary Numbers',
    'tellahmaneuver'    : 'The Tellah\nManeuver',
    '3point'            : 'The 3-Point System',
    'friendlyfire'      : 'Friendly Fire',
    'payablegolbez'     : 'Payable Golbez',
    'gottagofast'       : 'Gotta Go Fast',
    'worthfighting'     : 'Something Worth\nFighting For',
    'saveusbigchocobo'  : 'Save Us,\nBig Chocobo!',
    'isthisrandomized'  : 'Is This Even\nRandomized?',
    'forwardisback'     : 'Forward is\nthe New Back',
    'mirrormirror'      : 'Mirror, Mirror,\non the Wall',
    'doorsrando': 'Door Randomizer',
}

WACKY_ROM_ADDRESS = BusAddress(0x268000)
WACKY_RAM_ADDRESS = BusAddress(0x7e1660)
WACKY_LAST_AVAILABLE_ROM_ADDR = 0x26ffff # TODO: Find the actual limit
WACKY_LAST_AVAILABLE_RAM_BYTE = 0x7e166c

WACKY_RAM_USAGE = {
    'musical'           : 0,
    'bodyguard'         : 0,
    'fistfight'         : 0,
    'omnidextrous'      : 0,
    'biggermagnet'      : 0,
    'sixleggedrace'     : 0,
    'floorislava'       : 0,
    'neatfreak'         : 0,
    'timeismoney'       : 0,
    'nightmode'         : 0,
    'mysteryjuice'      : 0,
    'misspelled'        : 0,
    'enemyunknown'      : 0,
    'kleptomania'       : 0,
    'darts'             : 0,
    'unstackable'       : 0,
    'menarepigs'        : 13, # StatusEnforcement
    'skywarriors'       : 13, # StatusEnforcement
    'zombies'           : 13, # StatusEnforcement
    'afflicted'         : 13, # StatusEnforcement
    'batman'            : 0,
    'battlescars'       : 1,
    'imaginarynumbers'  : 0,
    'tellahmaneuver'    : 6,
    '3point'            : 0,
    'friendlyfire'      : 0,
    'payablegolbez'     : 3,
    'gottagofast'       : 0,
    'worthfighting'     : 2,
    'saveusbigchocobo'  : 0,
    'isthisrandomized'  : 0,
    'forwardisback'     : 0,
    'doorsrando'     : 0,
    'mirrormirror'      : 13, # StatusEnforcement
}

WACKY_MUTUAL_INCOMPATIBILITIES = [
    ['3point', 'battlescars', 'unstackable', 'afflicted', 'menarepigs', 'skywarriors', 'zombies', 'mirrormirror'], # These all use Wacky__InitializeAxtorHook
    ['afflicted', 'friendlyfire'], # These both use Wacky_SpellFilterHook
    ['battlescars', 'afflicted', 'zombies', 'worthfighting'], # These all use Wacky__PostBattleHook
    ['darts', 'musical'], # These both replace the Fight command
    ['3point','tellahmaneuver'], # These both mess with MP
]

def find_compatible_remaining_wacky_modes(current_modes):
    ram_bytes_used = 0
    total_ram_available = WACKY_LAST_AVAILABLE_RAM_BYTE - WACKY_RAM_ADDRESS.get_bus() + 1
    for wacky in current_modes:
        ram_bytes_used += WACKY_RAM_USAGE[wacky]
    remaining_challenges = set(WACKY_CHALLENGES.keys()) - set(current_modes)
    for group in WACKY_MUTUAL_INCOMPATIBILITIES:
        for wacky in current_modes:
            if wacky in group:
                remaining_challenges -= set(group)
                break
    # sets have no ordering, so we have to sort these to remain deterministic
    for wacky in sorted(remaining_challenges):
        if ram_bytes_used + WACKY_RAM_USAGE[wacky] > total_ram_available:
            remaining_challenges.remove(wacky)
    return sorted(remaining_challenges)


def setup(env):
    wacky_challenge = []
    if env.options.test_settings.get('wacky', None):
        wacky_challenge.append(env.options.test_settings['wacky'])
    # This keeps a reliable order and prevent duplicates. (Note that neither of those is actually necessary)
    for wacky in WACKY_CHALLENGES.keys():
        if env.options.flags.has(f'-wacky:{wacky}'):
            remaining_challenges = find_compatible_remaining_wacky_modes(wacky_challenge)
            if wacky not in remaining_challenges:
                raise Exception(f'Wacky mode {wacky} is incompatible with one or more of: {wacky_challenge}')
            wacky_challenge.append(wacky)

    random_count = 0
    max_random_count = 6
    for x in range(max_random_count, 0, -1):
        n = x if x > 1 else ''
        if env.options.flags.has(f'-wacky:random{n}'):
            random_count = x
            break

    for x in range(0, random_count):
        remaining_challenges = find_compatible_remaining_wacky_modes(wacky_challenge)
        if len(remaining_challenges) < 1:
            break
        choice = env.rnd.choice(remaining_challenges)
        wacky_challenge.append(choice)

    if len(wacky_challenge) > 0:
        env.meta['wacky_challenge'] = wacky_challenge

    for wacky in wacky_challenge:
        setup_func = globals().get(f'setup_{wacky}')
        if setup_func:
            setup_func(env)

def apply(env):
    wacky_challenge = env.meta.get('wacky_challenge', None)
    if wacky_challenge:
        env.add_file('scripts/wacky/wacky_common.f4c')
        env.add_substitution('intro disable', '')
        env.add_toggle('wacky_challenge_enabled')

        rom_base = WACKY_ROM_ADDRESS
        ram_base = WACKY_RAM_ADDRESS

        for idx, wacky in enumerate(wacky_challenge):
            # apply script of the same name, if it exists
            script_filename = f'scripts/wacky/{wacky}.f4c'
            if os.path.isfile(os.path.join(os.path.dirname(__file__), script_filename)):
                env.add_file(script_filename)

            env.add_script(f'''
                msfpatch {{ 
                    .def Wacky__ROMData_{wacky} ${rom_base.get_bus():06x} 
                    .def Wacky__RAM_{wacky}     ${ram_base.get_bus():06x}
                    }}
            ''')

            apply_func = globals().get(f'apply_{wacky}', None)
            if apply_func:
                rom_bytes_used = apply_func(env, rom_base) or 0
                ram_bytes_used = WACKY_RAM_USAGE[wacky]
                if rom_bytes_used:
                    if rom_base.get_bus() > WACKY_LAST_AVAILABLE_ROM_ADDR:
                        raise Exception(f"Incompatible wacky modes (too much ROM space required): {', '.join(wacky_challenge)}")
                    rom_base = rom_base.offset(rom_bytes_used)

                if ram_base.get_bus() + ram_bytes_used - 1 > WACKY_LAST_AVAILABLE_RAM_BYTE:
                    raise Exception(f"Incompatible wacky modes (RAM incompatibility): {', '.join(wacky_challenge)}")
                ram_base = ram_base.offset(ram_bytes_used)

            text = WACKY_CHALLENGES[wacky]
            centered_text = '\n'.join([line.center(26).upper().rstrip() for line in text.split('\n')])
            env.add_substitution(f'wacky challenge title {idx+1}', f'\n{centered_text}')
            env.add_toggle(f'wacky_challenge_{idx+1}')
            env.spoilers.add_table(f'WACKY CHALLENGE {idx+1}', [[text.replace('\n', ' ')]], public=env.options.flags.has_any('-spoil:all', '-spoil:misc'))



def apply_musical(env, rom_address):
    env.add_substitution('wacky_fightcommandreplacement', '#$08')

def apply_bodyguard(env, rom_address):
    # need substitution to mark all characters as cover-capable
    env.add_toggle('wacky_all_characters_cover')
    env.add_toggle('wacky_cover_check')

def apply_fistfight(env, rom_address):
    env.add_toggle('wacky_all_characters_ambidextrous')
    # change claws to be universally equippable, all other weapons not
    for item_id in range(0x01, 0x60):
        if item_id < 0x07:
            # is claw
            eqp_byte = 0x00
        elif item_id not in [0x3E, 0x46]: # ignore Spoon and custom weapon
            eqp_byte = 0x1F
        else:
            eqp_byte = None

        if eqp_byte is not None:
            env.add_binary(UnheaderedAddress(0x79106 + (0x08 * item_id)), [eqp_byte], as_script=True)

def apply_omnidextrous(env, rom_address):
    env.add_toggle('wacky_all_characters_ambidextrous')
    env.add_toggle('wacky_omnidextrous')

def apply_sixleggedrace(env, rom_address):
    env.add_toggle('wacky_challenge_show_detail')

def apply_neatfreak(env, rom_address):
    env.add_toggle('wacky_neatfreak')

def apply_timeismoney(env, rom_address):
    env.add_file('scripts/sell_zero.f4c')

def setup_mysteryjuice(env):
    juices = '''
        Sweet Sour Bitter Salty Spicy Fruity Minty Milky Creamy Meaty Tart Savory Buttery Purple Green Brown Clear Glowing Hot Cold Lukewarm Slushy Cloudy Smooth Gooey Lumpy Juicy Crunchy Chunky Muddy Runny Chewy Steamy Frothy Inky Murky Tasty Fancy Foamy Zesty Smoky Dry Wet Bubbly Fizzy Pungent Chalky Stringy Thick Gritty Gross Neon Bold Simple Shiny
        '''.split()
    env.rnd.shuffle(juices)
    
    JUICE_ITEMS = list(range(0xB0, 0xE2)) + [0xE4, 0xE5, 0xEB, 0xED]
    juice_mapping = {}
    juice_prices = env.meta.setdefault('altered_item_prices', {})
    for item_id in JUICE_ITEMS:
        juice_mapping[item_id] = '[potion]' + juices.pop()
        juice_prices[item_id] = 1000

    env.meta.setdefault('altered_item_names', {}).update(juice_mapping)
    env.meta['wacky_juices'] = juice_mapping

def apply_mysteryjuice(env, rom_address):
    ITEM_DESCRIPTION = (
        [0x00, 0xFA] + ([0xFF] * 27) + [0xFB, 0x00, 0x00] +
        [0x00, 0xFA] + ([0xFF] * 12) + ([0xC5] * 3) + ([0xFF] * 12) + [0xFB, 0x00, 0x00] +
        [0x00, 0xFA] + ([0xFF] * 27) + [0xFB, 0x00, 0x00] +
        [0x00, 0xFA] + ([0xFF] * 27) + [0xFB, 0x00, 0x00]
        )
    for item_id in env.meta['wacky_juices']:
        env.add_script(f'''
            text(item name ${item_id:02X}) {{{env.meta['wacky_juices'][item_id]}}}
        ''')
        env.meta.setdefault('item_description_overrides', {})[item_id] = ITEM_DESCRIPTION

def apply_misspelled(env, rom_address):
    spells_dbview = databases.get_spells_dbview()
    remappable_spells = spells_dbview.find_all(lambda sp: (sp.code >= 0x01 and sp.code <= 0x47 and sp.code not in [0x40,0x41]))
    shuffled_spells = list(remappable_spells)
    env.rnd.shuffle(shuffled_spells)

    # get summon effects and pair them with their summon spell
    raw_summon_effects = spells_dbview.find_all(lambda sp: (sp.code >=0x4D and sp.code <= 0x5D))
    summon_effects_list = list(raw_summon_effects)
    summon_effects_linked = {}
    for effect in summon_effects_list:
        # three Asuna effects
        if (effect.code in [0x5A, 0x5B, 0x5C]):
            try:
                summon_effects_linked[0x3E].append(effect)
            except:
                summon_effects_linked[0x3E] = [effect]
        # bahamut
        elif (effect.code == 0x5D):
            summon_effects_linked[0x3F] = effect
        else:
            summon_effects_linked[effect.code - 0x1C] = effect


    pairings = zip(remappable_spells, shuffled_spells)
    remap_data = [0x00] * 0x100
    for pair in pairings:
        remap_data[pair[0].code] = pair[1].code
        env.add_script(f'''
            text(spell name {pair[1].const}) {{{pair[0].name}}}
        ''')
        # rename effects of summon spells as well
        if (pair[1].code >= 0x31 and pair[1].code <= 0x3D):
            env.add_script(f'''
                text(spell name ${pair[1].code + 0x1C:02X}) {{{pair[0].name}}}
            ''')
        elif (pair[1].code == 0x3E):
            # three Asura effects
            env.add_script(f'''
                text(spell name $5A) {{{pair[0].name}}}
                text(spell name $5B) {{{pair[0].name}}}
                text(spell name $5C) {{{pair[0].name}}}
            ''')
        elif (pair[1].code == 0x3F):
            # bahamut
            env.add_script(f'''
                text(spell name $5D) {{{pair[0].name}}}
            ''')
        
        # trade MP costs
        env.add_binary(
            BusAddress(0xF97A5 + (0x06 * pair[1].code)),
            [(pair[0].data[5] & 0x7F) | (pair[1].data[5] & 0x80)],
            as_script=True
        )

        # trade summon effect MP costs as well
        if (pair[1].code >= 0x31 and pair[1].code <= 0x3D):
            env.add_binary(
                BusAddress(0xF97A5 + (0x06 * (pair[1].code + 0x1C))),
                [(pair[0].data[5] & 0x7F) | (summon_effects_linked[pair[1].code].data[5] & 0x80)],
                as_script=True
            )
        elif (pair[1].code == 0x3E):
            # three Asuna effects
            env.add_binary(
                BusAddress(0xF97A5 + (0x06 * 0x5A)),
                [(pair[0].data[5] & 0x7F) | (summon_effects_linked[0x3E][0].data[5] & 0x80)],
                as_script=True
            )
            env.add_binary(
                BusAddress(0xF97A5 + (0x06 * 0x5B)),
                [(pair[0].data[5] & 0x7F) | (summon_effects_linked[0x3E][1].data[5] & 0x80)],
                as_script=True
            )
            env.add_binary(
            BusAddress(0xF97A5 + (0x06 * 0x5C)),
            [(pair[0].data[5] & 0x7F) | (summon_effects_linked[0x3E][2].data[5] & 0x80)],
            as_script=True
            )
        elif (pair[1].code == 0x3F):
            # bahamut
            env.add_binary(
            BusAddress(0xF97A5 + (0x06 * 0x5D)),
            [(pair[0].data[5] & 0x7F) | (summon_effects_linked[0x3F].data[5] & 0x80)],
            as_script=True
            )   

    

    env.add_binary(rom_address, remap_data, as_script=True)
    env.add_toggle('wacky_misspelled')
    return len(remap_data)

def apply_kleptomania(env, rom_address):
    VANILLA_MONSTER_LEVELS = [3,5,5,4,5,20,19,4,6,5,5,6,6,6,6,6,7,23,7,7,8,8,9,36,16,25,12,9,21,9,11,14,97,19,10,10,11,12,23,48,15,8,8,16,12,15,16,13,16,31,17,20,20,79,17,17,15,18,18,34,20,20,35,15,27,20,20,21,21,41,22,22,41,25,44,49,27,26,35,32,28,79,28,29,39,14,14,28,25,29,29,32,32,33,34,43,26,27,34,32,30,31,53,31,50,33,39,96,40,35,67,42,23,36,37,45,43,23,39,32,40,48,26,58,40,40,44,48,98,30,50,98,36,37,96,16,60,60,61,34,97,40,45,54,99,61,97,32,99,99,30,71,99,61,62,98,97,54,98,99,99,10,10,2,15,15,15,9,9,9,16,15,15,16,16,16,26,36,31,47,31,7,32,32,25,15,15,50,53,79,47,37,63,79,79,19,5,48,48,63,96,96,47,5,31,17,1,1,1,1,15,15,47,79,63,63,63,1,31,31,31,31,1,3]
    items_dbview = databases.get_items_dbview()
    available_weapons = items_dbview.find_all(lambda it: it.category == 'weapon' and it.tier >= 2 and it.tier <= 8)
    available_armor = items_dbview.find_all(lambda it: it.category == 'armor' and it.tier >= 1 and it.tier <= 8)
    available_weapons.sort(key=lambda it: it.tier)
    available_armor.sort(key=lambda it: it.tier)

    is_armor_queue = [bool((i % 5) < 2) for i in range(len(VANILLA_MONSTER_LEVELS))]
    env.rnd.shuffle(is_armor_queue)

    equipment_bytes = []
    VARIATION = 0.05
    for monster_id,monster_level in enumerate(VANILLA_MONSTER_LEVELS):
        if is_armor_queue[monster_id]:
            available_items = available_armor
            scale = 30.0
        else:
            available_items = available_weapons
            scale = 50.0
        normalized_level = max(VARIATION, min(1.0 - VARIATION, monster_level / scale))

        variated_level = normalized_level + (env.rnd.random() - 0.50) * (VARIATION * 2.0)
        index = max(0, min(len(available_items) - 1, int(len(available_items) * variated_level)))
        item = available_items[index]
        equipment_bytes.append(item.code)

    env.add_binary(rom_address, equipment_bytes, as_script=True)
    return len(equipment_bytes)

def apply_darts(env, rom_address):
    env.add_substitution('wacky_fightcommandreplacement', '#$16')

def apply_unstackable(env, rom_address):
    env.add_toggle('wacky_unstackable')
    env.add_toggle('wacky_initialize_axtor_hook')

def apply_menarepigs(env, rom_address):
    env.add_toggle('wacky_initialize_axtor_hook')
    env.add_file('scripts/wacky/status_enforcement.f4c')
    env.add_toggle('wacky_status_enforcement_uses_job')

def apply_skywarriors(env, rom_address):
    env.add_toggle('wacky_initialize_axtor_hook')
    env.add_file('scripts/wacky/status_enforcement.f4c')

def apply_mirrormirror(env, rom_address):
    env.add_toggle('wacky_initialize_axtor_hook')
    env.add_file('scripts/wacky/status_enforcement.f4c')

def apply_zombies(env, rom_address):
    env.add_file('scripts/wacky/status_enforcement.f4c')
    env.add_toggle('wacky_initialize_axtor_hook')
    env.add_toggle('wacky_status_enforcement_uses_slot')
    env.add_toggle('wacky_status_enforcement_uses_battleinit_context')
    env.add_toggle('wacky_status_enforcement_uses_battle_context')
    env.add_toggle('wacky_post_battle_hook')

def apply_afflicted(env, rom_address):
    env.add_file('scripts/wacky/status_enforcement.f4c')
    env.add_toggle('wacky_initialize_axtor_hook')
    env.add_toggle('wacky_status_enforcement_uses_axtor')
    env.add_toggle('wacky_status_enforcement_uses_battleinit_context')
    env.add_toggle('wacky_spell_filter_hook')
    env.add_toggle('wacky_post_battle_hook')

    STATUSES = {
        'poison'  : [0x01, 0x00, 0x00, 0x00],
        'blind'   : [0x02, 0x00, 0x00, 0x00],
        'mute'    : [0x04, 0x00, 0x00, 0x00],
        'piggy'   : [0x08, 0x00, 0x00, 0x00],
        'mini'    : [0x10, 0x00, 0x00, 0x00],
        'toad'    : [0x20, 0x00, 0x00, 0x00],
        #'stone'   : [0x40, 0x00, 0x00, 0x00],
        'calcify' : [0x00, 0x01, 0x00, 0x00],
        'calcify2': [0x00, 0x02, 0x00, 0x00],
        'berserk' : [0x00, 0x04, 0x00, 0x00],
        'charm'   : [0x00, 0x08, 0x00, 0x00],
        #'sleep'   : [0x00, 0x10, 0x00, 0x00],
        #'stun'    : [0x00, 0x20, 0x00, 0x00],
        'float'   : [0x00, 0x40, 0x00, 0x00],
        'curse'   : [0x00, 0x80, 0x00, 0x00],
        'blink1'  : [0x00, 0x00, 0x00, 0x04],
        'blink2'  : [0x00, 0x00, 0x00, 0x08],
        'armor'   : [0x00, 0x00, 0x00, 0x10],
        'wall'    : [0x00, 0x00, 0x00, 0x20],
    }

    status_bytes = []
    for status in STATUSES:
        status_bytes.extend(STATUSES[status])    
    env.add_binary(rom_address, status_bytes, as_script=True)

    rng_table = [env.rnd.randint(0, len(STATUSES) - 1) for i in range(0x200)]
    env.add_binary(rom_address.offset(0x100), rng_table, as_script=True)
    return 0x100 + len(rng_table)


'''
def apply_afflicted_legacyversion(env):
    env.add_toggle('wacky_initialize_axtor_hook')
    env.add_file('scripts/wacky/status_enforcement.f4c')
    env.add_toggle('wacky_status_enforcement_uses_axtor')

    STATUSES = {
        'poison'  : [0x01, 0x00, 0x00, 0x00],
        'blind'   : [0x02, 0x00, 0x00, 0x00],
        'mute'    : [0x04, 0x00, 0x00, 0x00],
        'piggy'   : [0x08, 0x00, 0x00, 0x00],
        'mini'    : [0x10, 0x00, 0x00, 0x00],
        'toad'    : [0x20, 0x00, 0x00, 0x00],
        'calcify' : [0x00, 0x01, 0x00, 0x00],
        'calcify2': [0x00, 0x02, 0x00, 0x00],
        'berserk' : [0x00, 0x04, 0x00, 0x00],
        #'sleep'   : [0x00, 0x10, 0x00, 0x00],
        'float'   : [0x00, 0x40, 0x00, 0x00],
        'curse'   : [0x00, 0x80, 0x00, 0x00],
        'blink'   : [0x00, 0x00, 0x00, 0x08],
        'wall'    : [0x00, 0x00, 0x00, 0x20],
    }

    status_names = list(STATUSES)
    status_bytes = []
    for axtor_id in range(0x20):
        status = env.rnd.choice(status_names)
        status_bytes.extend(STATUSES[status])
    
    env.add_binary(WACKY_ROM_ADDRESS, status_bytes, as_script=True)
'''

def apply_battlescars(env, rom_address):
    env.add_toggle('wacky_initialize_axtor_hook')
    env.add_toggle('wacky_post_battle_hook')

def apply_tellahmaneuver(env, rom_address):
    env.add_toggle('wacky_omit_mp')

    # precalculate MP costs times 10
    spells_dbview = databases.get_spells_dbview()
    data = [0x00] * 0x400
    for spell_id in range(0x48):
        mp_cost = 10 * spells_dbview.find_one(lambda sp: sp.code == spell_id).mp
        data[spell_id] = mp_cost & 0xFF
        data[spell_id + 0x100] = (mp_cost >> 8) & 0xFF

    # also precalculate number * 10 in general
    for v in range(0x100):
        data[v + 0x200] = ((v * 10) & 0xFF)
        data[v + 0x300] = ((v * 10) >> 8) & 0xFF
    
    env.add_binary(rom_address, data, as_script=True)
    return len(data)

def apply_3point(env, rom_address):
    env.add_toggle('wacky_initialize_axtor_hook')

    # change all MP costs to 1
    spells_dbview = databases.get_spells_dbview()
    for spell_id in range(0x48):
        spell = spells_dbview.find_one(lambda sp: sp.code == spell_id)
        if spell.mp > 0:
            env.add_binary(
                BusAddress(0xF97A5 + (0x06 * spell_id)),
                [(spell.data[5] & 0x80) | 0x01],
                as_script=True
            )
    for spell_id in range(0x4D, 0x5E):
        spell = spells_dbview.find_one(lambda sp: sp.code == spell_id)
        env.add_binary(
            BusAddress(0xF97A5 + (0x06 * spell_id)),
            [(spell.data[5] & 0x80) | 0x01],
            as_script=True
        )

def apply_friendlyfire(env, rom_address):
    env.add_toggle('wacky_spell_filter_hook')
    env.add_file('scripts/wacky/spell_filter_hook.f4c')

def apply_payablegolbez(env, rom_address):
    BOSS_SLOT_HPS = {
        'antlion_slot' : 1000,
        'asura_slot' : 23000,
        'bahamut_slot' : 37000,
        'baigan_slot' : 4200,
        'calbrena_slot' : 8524,
        'cpu_slot' : 24000,
        'darkelf_slot' : 5000,
        'darkimp_slot' : 597,
        'dlunar_slot' : 42000,
        'dmist_slot' : 465,
        'elements_slot' : 65000,
        'evilwall_slot' : 19000,
        'fabulgauntlet_slot' : 1880,
        'golbez_slot' : 3002,
        'guard_slot' : 400,
        'kainazzo_slot' : 4000,
        'karate_slot' : 4000,
        'kingqueen_slot' : 6000,
        'leviatan_slot' : 35000,
        'lugae_slot' : 18943,
        'magus_slot' : 9000,
        'milon_slot' : 2780,
        'milonz_slot' : 3000,
        'mirrorcecil_slot' : 1000,
        'mombomb_slot' : 1250,
        'octomamm_slot' : 2350,
        'odin_slot' : 20500,
        'officer_slot' : 302,
        'ogopogo_slot' : 37000,
        'paledim_slot' : 27300,
        'plague_slot' : 28000,
        'rubicant_slot' : 25200,
        'valvalis_slot' : 6000,
        'wyvern_slot' : 25000,
    }
    bribe_values = []
    for slot in BOSS_SLOTS:
        bribe = BOSS_SLOT_HPS[slot] * 5
        bribe_values.extend([
            ((bribe >> (i * 8)) & 0xFF) for i in range(4)
        ])

    env.add_binary(rom_address, bribe_values, as_script=True)
    env.add_toggle('allow_boss_bypass')
    env.add_toggle('wacky_boss_skip_hook')
    return len(bribe_values)

def apply_gottagofast(env, rom_address):
    env.add_toggle('wacky_sprint')

def apply_worthfighting(env, rom_address):
    env.add_toggle('wacky_post_treasure_hook')
    env.add_toggle('wacky_post_battle_hook')

def apply_batman(env, rom_address):
    # Fun fact, we only get 10 digits to work with
    #  0123456789
    #  !ABFKMOPWZ
    # These letters give us:
    #  POP!  -> 7670
    #  POK!  -> 7640
    #  POW!  -> 7680
    #  OOF!  -> 6630
    #  WAM!  -> 8150
    #  WAK!  -> 8140
    #  WAP!  -> 8170
    #  ZAK!  -> 9140
    #  ZOK!  -> 9640
    #  ZAP!  -> 9170
    #  KOF!  -> 4630
    #  BOF!  -> 2630
    #  BOP!  -> 2670
    #  BAP!  -> 2170
    #  BAM!  -> 2150
    #  MOP!  -> 5670
    #  ZOO!  -> 9660
    #  KAK!  -> 4140
    #  KAF!  -> 4130
    #  OOP!  -> 6670
    #  ZAM!  -> 9150
    #  ZOW!  -> 9680
    #  ZZK!  -> 9940
    #  PAF!  -> 7130
    #  PAK!  -> 7140
    #  KOW!  -> 4680
    #  AWK!  -> 1840
    #  BAF!  -> 2130
    #  POF!  -> 7630
    #  OMF!  -> 6530
    #  OWW!  -> 6880
    data = [
        0x87, 0x86, 0x87, 0x80,
        0x87, 0x86, 0x84, 0x80,
        0x87, 0x86, 0x88, 0x80,
        0x86, 0x86, 0x83, 0x80,
        0x88, 0x81, 0x85, 0x80,
        0x88, 0x81, 0x84, 0x80,
        0x88, 0x81, 0x87, 0x80,
        0x89, 0x81, 0x84, 0x80,
        0x89, 0x86, 0x84, 0x80,
        0x89, 0x81, 0x87, 0x80,
        0x84, 0x86, 0x83, 0x80,
        0x82, 0x86, 0x83, 0x80,
        0x82, 0x86, 0x87, 0x80,
        0x82, 0x81, 0x87, 0x80,
        0x82, 0x81, 0x85, 0x80,
        0x85, 0x86, 0x87, 0x80,
        0x89, 0x86, 0x86, 0x80,
        0x84, 0x81, 0x84, 0x80,
        0x84, 0x81, 0x83, 0x80,
        0x86, 0x86, 0x87, 0x80,
        0x89, 0x81, 0x85, 0x80,
        0x89, 0x86, 0x88, 0x80,
        0x89, 0x89, 0x84, 0x80,
        0x87, 0x81, 0x83, 0x80,
        0x87, 0x81, 0x84, 0x80,
        0x84, 0x86, 0x88, 0x80,
        0x81, 0x88, 0x84, 0x80,
        0x82, 0x81, 0x83, 0x80,
        0x87, 0x86, 0x83, 0x80,
        0x86, 0x85, 0x83, 0x80,
        0x86, 0x88, 0x88, 0x80,
    ]
    env.add_binary(rom_address, data, as_script=True)
    return len(data)


def setup_saveusbigchocobo(env):
    env.meta['wacky_starter_kit'] = [( 'Carrot', [5] )]


def apply_doorsrando(env,rom_base):
    env.add_toggle('wacky_doorsrando')
    doors_rando.apply(env,rom_base)

