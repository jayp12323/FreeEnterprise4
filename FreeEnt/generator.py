import sys
import os
import re
import io
import random
import time
import struct
import zipfile
import hashlib
import glob
import json
import datetime
import uuid
import enum

import pyaes

import f4c

from f4c import encode_text

from .flags import FlagSet, FlagLogic
from .address import *
from .errors import *
from . import rewards
from .datablob import DataBlob

from . import spoilers

from . import core_rando
from . import keyitem_rando
from . import character_rando
from . import shop_rando
from . import treasure_rando
from . import boss_rando
from . import fusoya_rando
from . import encounter_rando
from . import dialogue_rando
from . import wyvern_rando
from . import odin_rando
from . import golbez_rando
from . import sprite_rando
from . import summons_rando
from . import objective_rando
from . import kit_rando
from . import custom_weapon_rando
from . import wacky_rando
from . import compile_item_prices
from . import doors_rando

from .script_preprocessor import ScriptPreprocessor

from . import version

from .util import Distribution

F4C_FILES = '''
    scripts/default.consts
    scripts/unused.f4c
    scripts/consts.f4c
    scripts/npcs.f4c
    scripts/characters.f4c
    scripts/doors.f4c
    scripts/items.f4c
    scripts/menu_data.f4c
    scripts/randomizer.f4c
    scripts/randomizer_keyitems.f4c
    scripts/japanese_names.f4c
    scripts/npc_text.f4c
    scripts/text_chars.f4c
    scripts/first_launch.f4c
    scripts/dialog_box_background.f4c
    scripts/bank00_extensions.f4c
    scripts/post_battle.f4c

    scripts/titlescreen.f4c
    scripts/opening.f4c
    scripts/mist.f4c
    scripts/damcyan.f4c
    scripts/antlion.f4c
    scripts/kaipo_rydia.f4c
    scripts/kaipo_rosa.f4c
    scripts/waterypass.f4c
    scripts/octomamm.f4c
    scripts/mthobs_rydia.f4c
    scripts/mthobs_yang.f4c
    scripts/fabul.f4c
    scripts/fabul_yangswife.f4c
    scripts/mysidia.f4c
    scripts/mtordeals.f4c
    scripts/baron_town.f4c
    scripts/baron_castle.f4c
    scripts/toroia.f4c
    scripts/toroia_edward.f4c
    scripts/magnes.f4c
    scripts/path_to_zot.f4c
    scripts/zot_magus.f4c
    scripts/zot_top.f4c
    scripts/agart.f4c
    scripts/adamant.f4c

    scripts/underworld.f4c
    scripts/dwarfcastle.f4c
    scripts/golbezshadow.f4c
    scripts/babil_lugae.f4c
    scripts/babil_cannon.f4c
    scripts/cave_eblan.f4c
    scripts/babil_rubicant.f4c
    scripts/babil_falcon.f4c
    scripts/sealed_cave.f4c
    scripts/sylph_cave.f4c
    scripts/feymarch.f4c
    scripts/baron_castle_odin.f4c
    scripts/mysidia_bigwhale.f4c

    scripts/bigwhale.f4c
    scripts/lunar_palace.f4c
    scripts/bahamut.f4c
    scripts/giant.f4c
    scripts/lunar_subterrane.f4c

    scripts/zeromus.f4c
    scripts/path_to_zeromus.f4c
    scripts/ending.f4c

    scripts/training_room.f4c
    scripts/dark_matter.f4c
    scripts/guided_intro.f4c
    scripts/hall_of_fame.f4c

    scripts/util.f4c
    scripts/text_buffers.f4c
    scripts/rewards.f4c
    scripts/objectives.f4c
    scripts/objective_data.f4c

    scripts/eventextensions.f4c
    scripts/eventextensions_if.f4c
    scripts/eventextensions_randomizer.f4c
    scripts/eventextensions_ending.f4c
    scripts/eventextensions_text.f4c
    scripts/eventextensions_misc.f4c

    scripts/dash.f4c
    scripts/fast_menus.f4c
    scripts/vfx00_clearchr.f4c
    scripts/actor_load_hybrid.f4c
    scripts/map_transitions.f4c
    scripts/call_orbs.f4c
    scripts/dynamic_party.f4c
    scripts/menu_kit.f4c
    scripts/long_call.f4c
    scripts/join_full_party_menu.f4c
    scripts/experience.f4c
    scripts/solo_battle.f4c
    scripts/dynamic_npc.f4c
    scripts/dynamic_npc_table.f4c
    scripts/extra_npc_palettes.f4c
    scripts/extra_item_descriptions.f4c
    scripts/stats.f4c
    scripts/level_up_summary.f4c
    scripts/treasure_discard.f4c
    scripts/treasure_character.f4c
    scripts/custom_item_effects.f4c
    scripts/config_init.f4c
    scripts/shadow_party.f4c
    scripts/fusoya_challenge.f4c
    scripts/experience_acceleration.f4c
    scripts/fix_airship_menu_softlock.f4c
    scripts/fix_edward_ghost_command.f4c
    scripts/fix_attack_power_overflow.f4c
    scripts/uptco_surprise.f4c
    scripts/sound_engine.f4c
    scripts/mute.f4c
    scripts/no_flashing.f4c
    scripts/hide_softlock_fixes.f4c
    scripts/rom_header.f4c
    scripts/sram_expansion.f4c
    scripts/character_expansion.f4c
    scripts/character_retrieval.f4c
    scripts/pregame_screen.f4c
    scripts/silly_names.f4c
    scripts/custom_menu.f4c
    scripts/tracker.f4c
    scripts/rosas_mom_hints.f4c
    scripts/mist_clip_fix.f4c
    scripts/status_text_fix.f4c
    scripts/fusoya_room.f4c
    scripts/no_save_point_message.f4c
    scripts/blank_textbox_fix.f4c
    scripts/cycle_party_leader.f4c
    scripts/item_delivery_quantity.f4c
'''
# the missing scripts/black_shirt_fix.f4c is included below as a conditional, if -wacky:whatsmygear is not on

BINARY_PATCHES = {
    0x117000 : 'binary_patches/standing_characters.bin',
    0x10da00 : 'assets/encounters/formation_average_levels_mod.bin', # differently generated average levels
}

class Generator:
    def __init__(self, options=None):
        self._options = (GeneratorOptions() if options is None else options)

    @property
    def options(self):
        return self._options

    def generate(self, romfile, force_recompile=False):
        return build(romfile, self._options, force_recompile)

class GeneratorOptions:
    def __init__(self):
        self.debug = False
        self.seed = str(int(time.time()) % 100000000)
        self.cache_path = None
        self.clean_cache = True
        self.quickstart = False
        #self.test_settings = {'quickstart': True, 'open': True, 'characters': True, 'items': True, 'gp': True}
        self.test_settings = dict()
        self.beta = False
        self.hide_flags = False
        self.spoiler_only = False

        self.flags = FlagSet()

    def get_version_str(self):
        version_str = 'v' + version.VERSION_STR
        if self.beta:
            version_str += '.b'
        return version_str

class GeneratorOutput:
    def __init__(self):
        self.rom = None
        self.seed = None
        self.version = None
        self.flags = None
        self.binary_flags = None
        self.report = None
        self.verification = None
        self.script = None
        self.public_spoiler = None
        self.private_spoiler = None

class Environment:
    def __init__(self, options, file_root=None):
        self._file_root = (os.path.dirname(__file__) if file_root is None else file_root)
        self._options = options
        self._meta = dict()
        self._rewards = rewards.RewardsAssignment()
        self._spoilers = spoilers.SpoilerLog()

        numeric_seed = int(hashlib.sha1(options.seed.encode('utf-8')).hexdigest(), 16)
        numeric_seed += int(hashlib.sha1(options.flags.to_string().encode('utf-8')).hexdigest(), 16)
        numeric_seed += int(hashlib.sha1(options.get_version_str().encode('utf-8')).hexdigest(), 16)
        if (options.test_settings or options.hide_flags) and not (options.debug):
            numeric_seed += int(hashlib.sha1(str(uuid.uuid4()).encode('utf-8')).hexdigest(), 16)
        elif options.flags.get_list(r'^-spoil:'):
            numeric_seed += int(hashlib.sha1(os.getenv('FE_SPOILER_SALT').encode('utf-8')).hexdigest(), 16)
        else:
            numeric_seed += int(hashlib.sha1(os.getenv('FE_SALT').encode('utf-8')).hexdigest(), 16)

        self._rnd_seed = numeric_seed
        
        self.rnd = random.Random()
        self.rnd.seed(numeric_seed)
        self._next_rnd_seed = self.rnd.getrandbits(32)

        self._substitutions = {}
        self._toggles = {}
        self._used_files = set()
        self._scripts = []
        self._binary_patches = {}
        self._assignments = {}

        self._pregame_text_lines = []
        self._blob = DataBlob()

    @property
    def options(self):
        return self._options

    @property
    def meta(self):
        return self._meta
    
    @property
    def substitutions(self):
        return self._substitutions

    @property
    def toggles(self):
        return self._toggles
    
    @property
    def scripts(self):
        return self._scripts
    
    @property
    def binary_patches(self):
        return self._binary_patches

    @property
    def rewards(self):
        return self._rewards
    
    @property
    def assignments(self):
        return self._assignments

    @property
    def spoilers(self):
        return self._spoilers

    @property
    def pregame_text_lines(self):
        return self._pregame_text_lines
    
    @property
    def numeric_seed(self):
        return self._rnd_seed

    @property
    def blob(self):
        return self._blob
    
    
    

    def update_assignments(self, update_dict):
        self._assignments.update(update_dict)
    
    def add_substitution(self, key, value):
        self._substitutions[key] = value

    def add_toggle(self, value):
        self._toggles[value] = True

    def add_script(self, script):
        self._scripts.append(script)

    def add_scripts(self, *scripts):
        self._scripts.extend(scripts)

    def add_binary(self, address, data, as_script=False):
        if type(address) is int:
            address = UnheaderedAddress(address)
        
        if as_script:
            lines = []
            lines.append(f'patch (${address.get_bus():06X} bus) {{')
            for i in range(0, len(data), 16):
                segment = data[i:i+16]
                lines.append('   ' + ' '.join([f'{b:02X}' for b in segment]))
            lines.append('}')
            self._scripts.append('\n'.join(lines))
        else:
            self._binary_patches[address.get_unheadered()] = data

    def add_file(self, filename):
        self.add_files(filename)

    def add_files(self, *filenames):
        for filename in filenames:
            if filename.lower() in self._used_files:
                # file already loaded
                continue
            self._used_files.add(filename.lower())

            with open(os.path.join(self._file_root, filename), 'r') as infile:
                script = f'// {filename}\n\n' + infile.read()
                self._scripts.append(script)

    def add_pregame_text(self, title, body, center=True, indent=1):
        MARGIN = 2
        if (title):
            if self._pregame_text_lines:
                self._pregame_text_lines.append('')
                self._pregame_text_lines.append('')
            self._pregame_text_lines.append((' ' * MARGIN) + title)
            self._pregame_text_lines.append('')

        lines = body.split('\n')
        if center:
            longest_length = max([len(l) for l in lines])
            prepad = ' ' * ((32 - longest_length) // 2)
        else:
            prepad = ' ' * (MARGIN + indent)

        self._pregame_text_lines.extend([prepad + l for l in lines])

    # returns a new RNG that is deterministic to the seed but operates
    # independently of the main RNG
    def get_independent_rnd(self):
        rnd = random.Random()
        rnd.seed(self._next_rnd_seed)
        self._next_rnd_seed = rnd.getrandbits(32)
        return rnd



#--------------------------------------------------------------------------
def _generate_title_screen_text(options):
    lines = [f"{options.get_version_str()}/{options.seed}"]
    
    if options.hide_flags:
        binary_flags = 'FLAGS HIDDEN'
    else:
        binary_flags = options.flags.to_binary()

    if len(binary_flags) > 28:
        cut_length = len(binary_flags) // 2
        lines.append(binary_flags[:cut_length])
        lines.append(binary_flags[cut_length:])
    else:
        lines.append(binary_flags)
        lines.append('')

    lines = [f"{l:^32}" for l in lines]
    text = ''.join(lines)

    data = []
    for c in text:
        if (len(data) >= 160):
            raise BuildError(f"_generate_title_screen_text: data exceeds allocated size in ROM")

        if c == ' ':
            data.append('FF 04')
        elif c == '.':
            data.append('FA 04')
        elif c == '!':
            data.append('FB 04')
        elif c == '/':
            data.append('FC 04')
        elif c == '-':
            data.append('FD 04')
        elif c == '_':
            data.append('FE 04')
        elif ord(c) >= ord('0') and ord(c) <= ord('9'):
            data.append('{:02X} 04'.format((ord(c) - ord('0')) + 0xF0))
        elif ord(c) >= ord('A') and ord(c) <= ord('Z'):
            data.append('{:02X} 04'.format((ord(c) - ord('A')) + 0xB0))
        elif ord(c) >= ord('a') and ord(c) <= ord('z'):
            data.append('{:02X} 04'.format((ord(c) - ord('a')) + 0xCA))
        else:
            data.append('00 00')
    return ' '.join(data)

#--------------------------------------------------------------------------
def _generate_pregame_screen_text(env):
    lines = []

    for l in env.pregame_text_lines:
        line_length = len(l)
        replacements = (re.findall('\[.*\]', l))
        for r in replacements:
            line_length -= len(r)-1
        lines.append(l + " " * (32 - line_length))

    info_bytes = []

    line_count = len(lines)
    info_bytes.append(line_count & 0xFF)
    info_bytes.append((line_count >> 8) & 0xFF)

    text_bytes = []

    for line in lines:
        line = line.replace('(', '[$cc]').replace(')', '[$cd]')
        line = line.replace('!', '[$7e]')
        line = line.replace('?', '[$7d]')
        tiles = f4c.encode_text(line)
        text_bytes.extend(tiles)

    text_length = len(text_bytes)
    info_bytes.append(text_length & 0xFF)
    info_bytes.append((text_length >> 8) & 0xFF)

    output_bytes = info_bytes + ([0x00] * (0x10 - len(info_bytes))) + text_bytes

    return ' '.join([f'{b:02X}' for b in output_bytes])




#--------------------------------------------------------------------------
def _generate_ending_version_text(options):
    binary_flags = options.flags.to_binary()
    lines = [options.get_version_str()]

    if len(binary_flags) > 22:
        lines.extend(binary_flags[i:i+22] for i in range(0, len(binary_flags), 22))
    else:
        lines.append(binary_flags)
        lines.append('')

    lines.append(options.seed)

    for i in range(len(lines)):
        line = lines[i]
        if line and not line.startswith('~'):
            padding_length = int((22 - len(line)) / 2)
            lines[i] = ('~' * padding_length) + line

    extra_lines = 9 - len(lines)
    lines.extend([''] * extra_lines)

    return '\n'.join(lines)

#--------------------------------------------------------------------------
CHECKSUM_TILES = [
    [0x23, 'mini'],
    [0x28, 'feather'],
    [0x29, 'claw'],
    [0x2B, 'staff'],
    [0x2E, 'sword'],
    [0x32, 'star'],
    [0x36, 'harp'],
    [0x37, 'bow'],
    [0x3B, 'shield'],
    [0x3E, 'glove'],
    [0x79, 'tent'],
    [0x7A, 'potion'],
    [0x7B, 'shirt'],
    [0x7C, 'ring'],
    [0x7D, 'crystal'],
    [0x7E, 'key'],
    ]

def _interpret_checksum(value):
    tiles = []
    for i in range(4):
        nibble = (value >> (i * 4)) & 0xF
        tiles.append(CHECKSUM_TILES[nibble])
    return tiles

def _generate_checksum_tiles(data):
    checksum = 0
    for b in data:
        checksum = (checksum >> 1) | ((checksum & 1) << 15)
        checksum += b

    return [CHECKSUM_TILES[(checksum >> (i * 4)) & 0xF] for i in range(4)], (checksum & 0xFFFF)

#--------------------------------------------------------------------------
def select_from_catalog(catalog_path, env):
    items = []
    with open(catalog_path, 'r') as infile:
        items = [l.strip() for l in infile if l.strip()]
    result = env.rnd.choice(items)
    return result

#--------------------------------------------------------------------------

def build(romfile, options, force_recompile=False):
    print(options.test_settings)
    flags_version = options.flags.get_version()
    if flags_version is not None and list(flags_version) != list(version.NUMERIC_VERSION):
        raise BuildError(f"Binary flag string is from a different version (got {'.'.join([str(v) for v in flags_version])}, needed {version.NUMERIC_VERSION})")

    logic_log = FlagLogic().fix(options.flags)
    errors = [log[1] for log in logic_log if log[0] == 'error']
    if errors:
        raise BuildError(f"Flag string error: {', '.join(errors)}")

    if options.test_settings.get('characters', False) and options.flags.has('Cbye'):
        options.flags.unset('Cbye')
    if options.test_settings.get('boss', None) and options.flags.has('Bvanilla'):
        options.flags.set('Bstandard')
    if options.test_settings.get('hobs', None) and options.flags.has('-vanilla:hobs'):
        options.flags.unset('-vanilla:hobs')


    env = Environment(options, os.path.dirname(__file__))

    formatted_flags = (env.options.flags.to_string(pretty=True, wrap_width=68).replace('\n', '\n            '))

    env.spoilers.add_raw(
        f"VERSION:    {env.options.get_version_str()}",
        '',
        f"FLAGS:      " + ('(hidden)' if env.options.hide_flags else formatted_flags),
        '',
        f"BINFLAGS:   " + ('(hidden)' if env.options.hide_flags else env.options.flags.to_binary()),
        '',
        f"SEED:       {env.options.seed}"
        )

    if env.options.hide_flags:
        env.spoilers.add_raw(f"HIDDEN INFO:",
        '',
        f"FLAGS:      " + formatted_flags, 
        '',
        f"BINFLAGS:   " + env.options.flags.to_binary(),
        public=False)

    env.add_files(*(F4C_FILES.split()))



    env.add_substitution('version_encoded', ''.join([f'{b:02X}' for b in f4c.encode_text(options.get_version_str())]))
    env.add_substitution('title_screen_text', _generate_title_screen_text(options))
    env.add_substitution('ending_version', _generate_ending_version_text(options))

    # write flag values directly into rom
    embedded_flags = [
        'objective_mode_classicforge',
        'objective_mode_classicgiant',
        'japanese_spells',
        'pass_in_shop',
        'bosses_standard',
        'no_free_characters',
        'no_free_key_item',
        'vanilla_fusoya',
        'characters_no_duplicates',
        'vanilla_agility',
        'characters_irretrievable',
        'objective_zeromus',
        'no_earned_characters',
        'no_starting_partner',
        ]
    flags_as_hex = []
    for slug in embedded_flags:
        set_flag = options.flags.has(slug)
        # disable talking to Edward if any no_free_key_item flag is set
        if (slug == 'no_free_key_item') and options.flags.has_any('no_free_key_item_dwarf', 'no_free_key_item_package'):
            set_flag = True
        flags_as_hex.append(1 if set_flag else 0)
    env.add_binary(BusAddress(0x21f0d0), flags_as_hex, as_script=True)

    # must be first
    wacky_rando.setup(env)

    if options.flags.has('drops_no_j'):
        env.add_file('scripts/adjust_us_drops.f4c')
    else:
        env.add_file('scripts/japanese_drops.f4c')

    if options.flags.has('japanese_spells'):
        env.add_file('scripts/japanese_spells.f4c')

    if options.flags.has('japanese_abilities'):
        env.add_file('scripts/japanese_abilities.f4c')

    RANDO_MODULES = [
        character_rando,
        core_rando,
        objective_rando,
        keyitem_rando,
        boss_rando,
        treasure_rando,
        shop_rando,
        fusoya_rando,
        encounter_rando,
        sprite_rando,
        summons_rando,
        wyvern_rando,
        odin_rando,
        golbez_rando,
        dialogue_rando,
        kit_rando,
        custom_weapon_rando
        ]

    for method_name in ['setup', 'apply', 'validate']:
        for module in RANDO_MODULES:
            try:
                method = getattr(module, method_name)
            except AttributeError:
                continue

            method(env)

    if not options.flags.has('vanilla_z') or options.flags.has('vintage'):
        ZEROMUS_PICS_DIR = os.path.join(os.path.dirname(__file__), 'compiled_zeromus_pics')
        if not options.flags.has('vanilla_z'):
            z_asset = select_from_catalog(os.path.join(ZEROMUS_PICS_DIR, 'catalog'), env)
            if options.flags.has('vintage'):
                z_asset += '.vintage'
            z_asset += '.asset'
        else:
            z_asset = 'ZeromNES.png.f4c'
        with open(os.path.join(ZEROMUS_PICS_DIR, z_asset), 'r') as infile:
            zeromus_sprite_script = infile.read()
        env.add_scripts('// [[[ ZEROMUS SPRITE START ]]]\n' + zeromus_sprite_script + '\n// [[[ ZEROMUS SPRITE END ]]]\n')

    env.add_file('scripts/midiharp.f4c')
    HARP_SONGS_DIR = os.path.join(os.path.dirname(__file__), 'compiled_songs')
    song_asset = select_from_catalog(os.path.join(HARP_SONGS_DIR, 'catalog'), env) + '.asset'
    env.add_substitution('midiharp default credits', '')
    with open(os.path.join(HARP_SONGS_DIR, song_asset), 'r') as infile:
        harp_script = infile.read()
    env.add_scripts('// [[[ HARP START ]]]\n' + harp_script + '\n// [[[ HARP END ]]]\n')

    # hack: add a block area to insert default names in rescript.py
    env.add_scripts('// [[[ NAMES START ]]]\n// [[[ NAMES END ]]]')

    if options.flags.has_any('no_free_key_item', 'no_free_key_item_package'):
        env.add_file('scripts/rydias_mom_slot.f4c')
    if options.flags.has('no_free_key_item_dwarf'):
        env.add_file('scripts/dwarf_hospital_slot.f4c')

    if options.flags.has('no_free_bosses'):
        env.add_substitution('free boss', '')
    else:
        env.add_substitution('no free boss', '')

    if options.flags.has('shops_free'):
        env.add_file('scripts/free_items.f4c')

    compile_item_prices.apply(env)

    env.add_substitution('default battle speed', '')

    if not options.flags.has('glitch_allow_duplication'):
        env.add_file('scripts/remove_item_duplication.f4c')
    if not options.flags.has('glitch_allow_mp_underflow'):
        env.add_file('scripts/remove_mp_underflow.f4c')
    if not options.flags.has('glitch_allow_dwarf_warp'):
        env.add_file('scripts/remove_dark_crystal_skip.f4c')
    if not options.flags.has('glitch_allow_life'):
        env.add_file('scripts/remove_life_glitch.f4c')
    if (not options.flags.has('glitch_allow_backrow')) or 'sixleggedrace' in env.meta.get('wacky_challenge', []):
        env.add_file('scripts/remove_backrow_glitch.f4c')

    # some part of this fix is always needed; substitutions within
    # this file handle whether the glitch is fully "fixed"
    env.add_file('scripts/sylph_odin_mp_fix.f4c')

    if options.flags.has('edward_spoon'):
        env.add_file('scripts/edward_spoon.f4c')

    if options.flags.has('give_monsters_evade'):
        env.add_file('scripts/give_monsters_evade.f4c')
    
    if options.flags.has('let_monsters_flee'):
        env.add_file('scripts/monster_flee.f4c')

    # experience flag substitutions and toggles
    # split, noboost, nokeyboost, crystalbonus, and maxlevelbonus are all handled directly via f4c scripts
    exp_objective_bonus = env.options.flags.get_suffix('-exp:objectivebonus')
    if exp_objective_bonus:
        if not (exp_objective_bonus == '_num'):
            exp_objective_bonus = 100 // int(exp_objective_bonus)
            env.add_substitution('experience objective bonus divisor', f'#${exp_objective_bonus:02X}')
        else:
            num_obj = env.substitutions['objective count']
            env.add_substitution('experience objective bonus divisor', '#$' + num_obj)
        env.add_toggle('experience_objective_bonus')

    exp_kicheck_bonus = env.options.flags.get_suffix('-exp:kicheckbonus')
    if exp_kicheck_bonus:
        if not (exp_kicheck_bonus == '_num'):
            exp_kicheck_bonus = 100 // int(exp_kicheck_bonus)
            env.add_substitution('experience key item check bonus divisor', f'#${exp_kicheck_bonus:02X}')
        else:
            num_kichecks = env.meta['number_key_item_slots']
            # subtract 1 in the following substitution to skip the starting KI check
            env.add_substitution('experience key item check bonus divisor', f'#${(num_kichecks-1):02X}')
        env.add_toggle('experience_kicheck_bonus')

    exp_zonk_bonus = env.options.flags.get_suffix('-exp:zonkbonus')
    if exp_zonk_bonus:
        exp_zonk_bonus = 100 // int(exp_zonk_bonus)
        # need to check for the starting key item here, using the rewards assignment;
        # cannot count starting non-KI as a zonk, so also ignore starting KI if necessary
        if (env.meta['rewards_assignment'])[rewards.RewardSlot.starting_item].is_key: 
            env.add_substitution('starting key item zonk', '#$01')
        else:
            env.add_substitution('starting key item zonk', '#$00')
        env.add_substitution('experience zonk bonus divisor', f'#${exp_zonk_bonus:02X}')
        env.add_toggle('experience_zonk_bonus')

    exp_miab_bonus = env.options.flags.get_suffix('-exp:miabbonus')
    if exp_miab_bonus:
        exp_miab_bonus = int(exp_miab_bonus) // 50
        env.add_substitution('experience miab bonus multiplier', f'#${exp_miab_bonus:04X}')
        env.add_toggle('experience_miab_bonus')

    exp_moon_bonus = env.options.flags.get_suffix('-exp:moonbonus')
    if exp_moon_bonus:
        exp_moon_bonus = int(exp_miab_bonus) // 100
        env.add_substitution('experience moon bonus multiplier', f'#${exp_miab_bonus:04X}')
        env.add_toggle('experience_moon_bonus')

    exp_geometric_mod = env.options.flags.get_suffix('-exp:geometric')
    if exp_geometric_mod:
        exp_geometric_mod = int(exp_geometric_mod) // 10
        env.add_substitution('experience geometric numerator', f'        lda #${exp_geometric_mod:02X}')
        env.add_toggle('experience_geometric')

    if options.flags.has('vintage'):
        env.add_files(
            'scripts/vintage_battlefield.f4c',
            'scripts/vintage_palettes.f4c',
            'scripts/vintage_sound.f4c'
            )
        env.add_substitution('vintage shoutout', '~~~~~~~~~~~~and FF1R')

    if options.flags.has('jump'):
        env.add_file('scripts/jump.f4c')

    # misc/creative tweaks
    if options.flags.has('kainmagic'):
        env.add_file('scripts/give_kain_magic.f4c')
    if options.flags.has('edwardheal'):
        env.add_file('scripts/improve_edward_heal.f4c')

    if not options.hide_flags:
        env.add_substitution('flags hidden', '')
    is_doorsrando=options.flags.get_list(r'(doors|entrances)rando')

    if is_doorsrando:
        rando_scope,rando_type = is_doorsrando[0].split(":")
        env.add_file('scripts/map_history_extension.f4c')
        env.add_file('scripts/doorsrando.f4c')
        env.add_toggle('doorsrando')
        doors_rando.apply(env, rando_scope,rando_type)

    # must be last
    wacky_rando.apply(env)
    # finalize rewards table
    rewards_data = env.meta['rewards_assignment'].generate_table()
    # for reward in env.meta['rewards_assignment']:
    #     print(f'Rewards data is '+str(reward) + ' with value ' + str(int(reward)))
    #print(f' Final rewards data {rewards_data}')
    env.blob.add('Rewards__Table', rewards_data)

    # generate blob and defines
    blob_address = 0x258000
    blob_data, blob_defines = env.blob.generate(0x8000, blob_address, rnd=(None if env.options.debug else env.rnd))

    env.add_binary(BusAddress(blob_address), blob_data)
    env.add_script('msfpatch {\n'
        + '\n'.join([f'.def {k} ${blob_defines[k]:06X}' for k in blob_defines])
        + '\n}')

    # item descriptions
    with open(os.path.join(os.path.dirname(__file__), 'assets/item_info/item_descriptions.bin'), 'rb') as infile:
        item_description_data = list(infile.read())
    for item_id in env.meta.get('item_description_overrides', {}):
        item_description_override = env.meta['item_description_overrides'][item_id]

        # 128 bytes per item description
        for i in range(len(item_description_override)):
            item_description_data[0x80 * item_id + i] = item_description_override[i]

    # overwrite lines 2-4 of the descriptions of gear with wacky-specific text
    if 'whatsmygear' in env.meta.get('wacky_challenge',[]):
        for item_id in range(0,176):
            # skip 0x00 (no weapon) and 0x60 (no armour) because their descriptions will be hidden anyway
            if item_id in [0,96]:
                continue
            item_description_data[0x80 * item_id + 0x20 : 0x80 * item_id + 0x80] = env.meta['wacky_gear_descriptions'][item_id]
    else:
        env.add_file('scripts/black_shirt_fix.f4c') # cannot double-patch the Black Shirt!
    
    env.add_binary(UnheaderedAddress(0x120000), item_description_data)

    # pregame text
    if env.options.hide_flags:
        env.add_pregame_text('FLAGS', 'hidden')
    else:
        env.add_pregame_text('FLAGS', env.options.flags.to_string(pretty=True, wrap_width=26), center=False)
        
    pregame_bytes = _generate_pregame_screen_text(env)
    env.add_substitution('pregame_screen_text', pregame_bytes)

    if options.debug:
        with open(os.path.join(os.path.dirname(__file__), 'scripts/debug_init.f4c'), 'r') as infile:
            env.add_substitution('debug init', infile.read())
        env.add_substitution('debug disable', '')
    else:
        env.add_substitution('debug enable', '')

    if options.test_settings:
        env.add_files('scripts/testmode.f4c')

        # TODO: move out into separate file
        if 'boss' in options.test_settings:
            for force_slot in options.test_settings['boss']:
                env.add_scripts('''
                    npc(#TrainingRoomSoldierOutside)
                    {
                        eventcall {
                            $F8
                        }
                    }

                    event($F8) {
                        [#B #Rando_BossBattle #rando.<SLOT_NAME>]
                    }
                    '''.replace('<SLOT_NAME>', force_slot))
                break

        if 'noboss' in options.test_settings:
            env.add_toggle('force_boss_bypass')
    else:
        env.add_substitution('testmode', '')

    if not (options.quickstart or options.test_settings.get('quickstart', False)):
        env.add_substitution('quickstart', '')

    scripts = []
    script_preprocessor = ScriptPreprocessor(env)
    for script in env.scripts:
        scripts.append(script_preprocessor.preprocess(script))

    if options.debug:
        with open(os.path.join(os.path.dirname(__file__), 'scripts/sandbox.f4c'), 'r') as infile:
            scripts.append(script_preprocessor.preprocess(infile.read()))

    for addr in BINARY_PATCHES:
        with open(os.path.join(os.path.dirname(__file__), BINARY_PATCHES[addr]), 'rb') as infile:
            data = infile.read()
        env.add_binary(UnheaderedAddress(addr), data)

    bytes_patches = []
    for addr in env.binary_patches:
        data = env.binary_patches[addr]
        bytes_patch = f4c.BytesPatch(data, unheadered_address=addr)
        bytes_patches.append(bytes_patch)

    embedded_script = f'''/*
        {options.get_version_str()}
        {options.flags.to_string()}
        {options.seed}
        \n''' + '\n'.join(['{} <- {}'.format((k.name if issubclass(type(k), enum.IntEnum) else str(k)), env.assignments[k]) for k in env.assignments]) + '\n*/'
    embedded_script += '\n//----------------------------------------\n'
    embedded_script += '\n//---------\n'.join(scripts)
    embedded_script_utf8 = embedded_script.encode('utf-8')

    metadata_doc = {
        'version' : options.get_version_str(),
        'flags' : ('(hidden)' if options.hide_flags else options.flags.to_string()),
        'binary_flags' : ('(hidden)' if options.hide_flags else options.flags.to_binary()),
        'seed' : options.seed,
        }
    if env.meta.get('objective_descriptions', None):
        metadata_doc['objectives'] = env.meta['objective_descriptions']
    
    embedded_metadata_doc = json.dumps(metadata_doc).encode('utf-8')
    bytes_patches.append(f4c.BytesPatch(
        struct.pack('<L', len(embedded_metadata_doc)) + embedded_metadata_doc,
        unheadered_address=0x1FF000
        ))

    # note areas of raw binary patches so that rescript can find them
    bytes_patch_scripts = []
    for bytes_patch in bytes_patches:
        addr = bytes_patch.get_unheadered_address()
        bytes_patch_scripts.append(f'// RAWPATCH:{addr:X},{len(bytes_patch.data):X}')
    bytes_patch_scripts = '\n'.join(bytes_patch_scripts) + '\n'
    embedded_script += bytes_patch_scripts
    embedded_script_utf8 += bytes_patch_scripts.encode('utf-8')

    zip_info = zipfile.ZipInfo(filename='script.f4c', date_time=(2000,1,1,0,0,0))
    zip_info.compress_type = zipfile.ZIP_LZMA
    zip_buffer = io.BytesIO()
    report_zip = zipfile.ZipFile(zip_buffer, mode='w')
    report_zip.writestr(zip_info, embedded_script_utf8)
    report_zip.close()

    zip_buffer.seek(0)
    embedded_report = zip_buffer.read()

    key = os.getenv('FE_EMBEDDED_REPORT_KEY').encode("utf-8")
    aes = pyaes.AESModeOfOperationCTR(key)
    encrypted_report = aes.encrypt(embedded_report)

    report_addr = 0x1FF000 - len(encrypted_report) - 4
    scripts.append(f4c.BytesPatch(
        encrypted_report + struct.pack('<L', len(encrypted_report)), 
        unheadered_address=report_addr
        ))

    compile_options = f4c.CompileOptions()
    compile_options.build_cache_path = options.cache_path
    compile_options.clean_cache = options.clean_cache
    compile_options.force_recompile = force_recompile
    if not options.debug:
        compile_options.shuffle_msfpatches = True
        compile_options.random_seed = env.numeric_seed

    if options.spoiler_only:
        compile_report = None
        rom_data = bytes()
        rom_checksum = 0
    else:
        output_buffer = io.BytesIO()
        compile_report = f4c.compile(romfile, output_buffer, *scripts, *bytes_patches, options=compile_options)

        output_buffer.seek(0)
        rom_data = output_buffer.read()
        rom_checksum = rom_data[0x007FDE] | (rom_data[0x007FDF] << 8)

    build_output = GeneratorOutput()
    build_output.rom = rom_data
    build_output.seed = metadata_doc['seed']
    build_output.version = metadata_doc['version']
    build_output.flags = options.flags.to_string() # metadata doc may contain "hidden" for flags, so can't reuse
    build_output.binary_flags = options.flags.to_binary()
    build_output.verification = [c[1] for c in _interpret_checksum(rom_checksum)]
    build_output.report = compile_report
    build_output.script = embedded_script

    if env.options.flags.get_list(r'^-spoil:'):
        sparse_spoiler_flags = env.options.flags.get_list(r'^-spoil:sparse')
        if sparse_spoiler_flags:
            sparsity = int(sparse_spoiler_flags[0][len('-spoil:sparse'):])
            env.spoilers.sparisfy(sparsity, env.rnd)
        build_output.public_spoiler = env.spoilers.compile(public=True)
    else:
        build_output.public_spoiler = None

    build_output.private_spoiler = env.spoilers.compile(public=False)
    
    
    return build_output


#--------------------------------------------------------------------------

