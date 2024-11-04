from . import databases
from . import address

POSSIBLE_BIGBANG_COMMANDS = {
    '#spell.Quake' : 'all characters',
    '#spell.Meteo' : 'all characters', # needs spell power adjustment for no-nerfs
    '#spell.Enemy_Charm' : 'all characters',
    '#spell.Enemy_Whisper' : 'all characters',
    '#spell.Enemy_Storm' : 'all characters',
    '#spell.Enemy_Blitz' : 'all characters',
    '#spell.Enemy_Blizzard' : 'all characters',
    '#spell.Enemy_Glare' : 'all characters',
    '#spell.Enemy_Wave' : 'all characters',
    '#spell.Enemy_Tornado' : 'all characters',
    '#spell.Enemy_Laser' : 'all characters',
    '#spell.Enemy_Odin' : 'all characters',
    '#spell.Enemy_Globe199' : 'all characters', # needs spell power adjustment for no-nerfs
    '#spell.Enemy_BigBang' : 'all characters',
    '#spell.Enemy_MegaNuke' : 'all characters',
}

BIGBANG_5_COMMANDS = {
    '#spell.Enemy_Count' : 'all characters', # battle-cheesing but it's fine if it's only the very last BB
    '#spell.Enemy_Dancing' : 'all characters', # script-breaking but it's fine if it's only the very last BB
}

def apply(env):
    if not env.options.flags.has_any('z_physical_script','z_physical_or_magical_script','z_random_bigbangs','z_random_phases','z_no_nerfs','z_must_nerf'):
        return
    
    bigbang_replacements = [[], [], [], [], [], []]
    script_nuke_replacement = []
    script_virus_replacement = []
    meteo_replacement = []
    counter_nuke_replacement = []
    counter_nuke_call_replacement = []
    counter_weak_replacement = []
    counter_virus_replacement = []
    stat_changes = ['monster($C9)\n', '{\n']
    scriptchangeflag = False
    statchangeflag = False

    if env.options.flags.has('z_physical_script') or ((env.rnd.random() < 1/2) and env.options.flags.has('z_physical_or_magical_script')):
        scriptchangeflag = True
        statchangeflag = True
        env.add_toggle("physical_z_fight_fixes")
        # repurpose attack index $5D to be (20, 99, 200) and $5E to be (18, 99, 255), set Z's base attack index to be $5D
        # ......... do I want to give Z an attack element? ... like *Drain*? lmao. No, but that'd be wild.
        env.add_binary(address.UnheaderedAddress(0x072497), [0x14, 0x63, 0xC8])
        env.add_binary(address.UnheaderedAddress(0x07249A), [0x12, 0x63, 0xFF])
        # use a different attack index under z_must_nerf:
        if env.options.flags.has('z_must_nerf'):
            stat_changes.append('    attack index $9F\n') # (255, 99, 255)
        else:
            stat_changes.append('    attack index $5D\n')
        bb014_attack_index = ('$9F' if env.options.flags.has('z_must_nerf') else '$5D')
        bb235_attack_index = ('$9F' if env.options.flags.has('z_must_nerf') else '$5E')

        if env.options.flags.has('z_no_nerfs'):
            bigbang_replacements[0].extend([
                '    chain {\n',
                '        set attack index $5D\n',
                '        chain into\n',
                '        use command #DarkWave\n',
                '        condition 3\n'
                '    }\n',
            ])
            for i in [1, 4]:
                bigbang_replacements[i].extend([
                    '    chain {\n',
                    '        set attack index $5D\n',
                    '        chain into\n',
                    '        use command #DarkWave\n',
                    '    }\n',
                ])
            for i in [2, 3, 5]:
                bigbang_replacements[i].extend([
                    '    chain {\n',
                    '        set attack index $5E\n',
                    '        chain into\n',
                    '        use command #DarkWave\n',
                    '    }\n',
                ])  
        else:
            bigbang_replacements[0].extend([
                '    use command #DarkWave\n',
                '    condition 3\n'
            ])
            for i in [1, 4]:
                bigbang_replacements[i].extend([
                    '    set attack index ' + bb014_attack_index + '\n',
                    '    use command #DarkWave\n',
                ])
            for i in [2, 3, 5]:
                bigbang_replacements[i].extend([
                    '    set attack index ' + bb235_attack_index + '\n',
                    '    use command #DarkWave\n',
                ])

        # Yes, this works, but only because we wrote a bugfix for retargetting spells 
        script_nuke_replacement.extend([
            '    set attack index $5F\n',
            '    use command #Jump\n',
        ])
        script_virus_replacement.extend([
            '    set attack index $41\n',
            '    target all characters\n',
            '    use #spell.Enemy_Needle\n',
        ])
        # already in a chain
        meteo_replacement.extend([
            '    set attack index $4E\n',
            '    pass\n\n',
            '    use command #DarkWave\n',
        ])
        # new Fight counter, intended to allow nerfing of Dark Wave; script 0x4D
        counter_nuke_replacement.extend([ 
            '    set attack index $41\n',
            '    fight\n',
        ])
        # new Dart counter, strong Needle, nerfs Dark Wave a little bit; script 0x4E
        counter_nuke_call_replacement.extend([ 
            '    set attack index $5F\n',
            '    use #spell.Enemy_Counter\n',
        ])
        # new Jump counter, brutally very strong Fight, reverse nerf (like Virus does for normal Big Bang); script 0x4F
        counter_weak_replacement.extend([ 
            '    set attack index $5E\n',
            '    fight \n', 
        ])
        # new Aim counter, intended to allow nerfing of Dark Wave; script 0x58
        counter_virus_replacement.extend([ 
            '    set attack index $41\n',
            '    target all characters\n',
            '    use #spell.Enemy_Counter\n',  
        ])

        # custom react-to-dart condition: 0x16 is Dart, so... add 0xC0 to it? yep, works perfectly. 
        # overwriting index 0x05, which is unused; condition set 0x05 points at condition 0x05, so we just use that
        env.add_binary(address.UnheaderedAddress(0x076700 + (0x05 * 0x4)), [0x08, 0x00, 0xD6, 0x00])
        # custom react-to-aim condition: 0x0C is Aim, so... add 0xC0 to it? yep, works perfectly. overwriting index 0x29, which is unused
        # condition 0x29 is only used in condition set 0x30, so we just use that
        env.add_binary(address.UnheaderedAddress(0x076700 + (0x29 * 0x04)), [0x08, 0x00, 0xCC, 0x00])
        # for reactions: first two are vanilla, third is custom react-to-Dart, fourth is custom react-to-Aim, fifth is react-to-Jump (Land), sixth is react-to-Fight
        # will need to change in the event of writing a compiler for new ai sets/etc.
        env.add_binary(address.UnheaderedAddress(0x0764A1), [0x61, 0x56, 0x18, 0x54, 0x05, 0x4E, 0x30, 0x58, 0x5C, 0x4F, 0x06, 0x4D]) 
    
    elif env.options.flags.has('z_random_bigbangs'):
        scriptchangeflag = True
        commands = list(POSSIBLE_BIGBANG_COMMANDS)
        replacement_commands = []
        for i in range(0,5):
            replacement_commands.append(commands[env.rnd.randrange(0,len(commands))])
        # the last Big Bang can have some funnier commands
        commands.extend(list(BIGBANG_5_COMMANDS))
        replacement_commands.append(commands[env.rnd.randrange(0,len(commands))])

        # use a different spell power under z_must_nerf:
        # setting 255 at the start via the script-change f4c, 253 for scripted changes because 254/255 break things
        if env.options.flags.has('z_must_nerf'):
            statchangeflag = True
            stat_changes.append('    spell power 255\n')
        bb_spell_powers = []
        for i in range(0,6):
            if env.options.flags.has('z_no_nerfs') and replacement_commands[i] == '#spell.Meteo':
                bb_spell_powers.append('9')
            elif env.options.flags.has('z_no_nerfs') and replacement_commands[i] == '#spell.Enemy_Globe199':
                bb_spell_powers.append('20')
            elif env.options.flags.has('z_must_nerf'):
                bb_spell_powers.append('253')
            elif i in [0, 1, 4]:
                bb_spell_powers.append('31')
            else:
                bb_spell_powers.append('32')

        bigbang_replacements[0].extend([
            '    target all characters\n',
            '    use ' + replacement_commands[0] + '\n',
            '    condition 3\n'
        ])
        for i in [1, 4]:
            bigbang_replacements[i].extend([
                '    set spell power ' + bb_spell_powers[i] + '\n',
                '    target all characters\n',
                '    use ' + replacement_commands[i] + '\n',
            ])
        for i in [2, 3, 5]:
            bigbang_replacements[i].extend([
                '    set spell power ' + bb_spell_powers[i] + '\n',
                '    target all characters\n',
                '    use ' + replacement_commands[i] + '\n',
            ])

        if env.options.flags.has('z_no_nerfs'):
            for i in range(0,6):
                bigbang_replacements[i] = ['    ' + bigbang_replacements[i][k] for k in range(0,len(bigbang_replacements[i]))]
            bigbang_replacements[0].insert(0, '    chain {\n')
            bigbang_replacements[0].insert(1, '        set spell power ' + bb_spell_powers[0] + '\n')
            bigbang_replacements[0].insert(2, '        chain into\n')
            bigbang_replacements[0].append('    }\n')
            for i in range(1,6):
                bigbang_replacements[i].insert(0, '    chain {\n')
                bigbang_replacements[i].insert(2, '        chain into\n')
                bigbang_replacements[i].append('    }\n')

        env.spoilers.add_table(
            "MISC", 
            [ ("Opening Big Bang replacement", databases.get_spell_spoiler_name(replacement_commands[0])),
              ("Virus phase Big Bang replacements", ', '.join([databases.get_spell_spoiler_name(replacement_commands[i]) for i in range(1,4)])),
              ("Nuke phase Big Bang replacements", ', '.join([databases.get_spell_spoiler_name(replacement_commands[i]) for i in range(4,6)])) ],
            public = env.options.flags.has_any('-spoil:all', '-spoil:misc')
            )
        
    elif env.options.flags.has('z_no_nerfs'): 
        # vanilla script but with chains for the Big Bangs; yes, this will be brutal
        scriptchangeflag = True
        bigbang_replacements[0].extend([
            '    chain {\n',
            '        set spell power 31\n',
            '        chain into\n',
            '        use #Enemy_BigBang\n',       
            '        condition 3\n'
            '    }\n'
        ])
        for i in [1, 4]:
            bigbang_replacements[i].extend([
                '    chain {\n',
                '        set spell power 31\n',
                '        chain into\n',
                '        use #Enemy_BigBang\n',
                '    }\n'
            ])
        for i in [2, 3, 5]:
            bigbang_replacements[i].extend([
                '    chain {\n',
                '        set spell power 32\n',
                '        chain into\n',
                '        use #Enemy_BigBang\n',
                '    }\n'
            ])
    
    elif env.options.flags.has('z_must_nerf'):
        # vanilla script except we make the spell power set to 253 (0xFD) for Big Bangs
        # setting 255 at the start via the script-change f4c
        # I *think* using 255 (0xFF) makes the game think it's an opcode... yep. so does 254 (0xFE), so 253 it is.
        scriptchangeflag = True
        statchangeflag = True
        stat_changes.append('    spell power 255\n')
        
        for i in [1, 4]:
            bigbang_replacements[i].extend([
                '    set spell power 253\n',
                '    use #Enemy_BigBang\n',
            ])
        for i in [2, 3, 5]:
            bigbang_replacements[i].extend([
                '    set spell power 253\n',
                '    use #Enemy_BigBang\n',
            ])        

    if env.options.flags.has('z_random_phases'):
        phases = [0x4C, 0x55, 0x57]
        env.rnd.shuffle(phases)
        # manual bytes for attack phase shuffle:
        env.add_binary(address.UnheaderedAddress(0x076498), [0x15, phases[2], 0x14, phases[1], 0x13, phases[0], 0x00, 0x4B])

    # now add the script changes as substitutions, and add the script change f4c
    for i in range(0,6):
        if bigbang_replacements[i]:
            env.add_substitution(f'big bang {i+1} replacement', ''.join(bigbang_replacements[i]))
    if script_nuke_replacement:
        env.add_substitution('script virus replacement', ''.join(script_virus_replacement))
        env.add_substitution('script nuke replacement', ''.join(script_nuke_replacement))
    if counter_nuke_replacement:
        env.add_substitution('counter nuke replacement', ''.join(counter_nuke_replacement))
        env.add_substitution('counter virus replacement', ''.join(counter_virus_replacement))
        env.add_substitution('counter weak replacement', ''.join(counter_weak_replacement))
        env.add_substitution('counter nuke call replacement', ''.join(counter_nuke_call_replacement))
    if meteo_replacement:
        env.add_substitution('meteo replacement', ''.join(meteo_replacement))
    if scriptchangeflag:
        env.add_file('scripts/zeromus_scriptchange.f4c')
    if statchangeflag:
        stat_changes.append('}\n')
        env.add_substitution('Z base stat changes', ''.join(stat_changes))