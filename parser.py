import json

GAME_TITLE = 'My ROMHack'

MOVES_FILE = 'Moves.txt'
POKS_FILE = 'Personal Entries.txt'
LEVELUP_FILE = 'Level Up Moves.txt'
TRAINERS_FILE = 'Battles.txt'

REPLACED_POKS_FILE = 'replaced_poks.txt'
FORMS_FILE = 'forms.txt'

OUTPUT_FILE = 'output.json'

#region Moves Data
with open(MOVES_FILE, 'r', encoding = 'utf-16') as file:
    moves_lines = file.readlines()
    
moves_data = {}
for line in moves_lines:
    line = line.strip()
    
    # each line has a move - a move is always only one line
    data = line.split(' | ')
    name = data[0]
    type = data[1]
    bp = data[2]
    cat = data[3]
    
    moves_data[name] = {
        'type'      : type,
        'basePower' : int(bp),
        'category'  : cat,
    }
#endregion Moves Data

#region Poks Data
with open(REPLACED_POKS_FILE, 'r') as file:
    replaced_poks_lines = file.readlines()

replaced_poks = {}
for line in replaced_poks_lines:
    line = line.strip()
    
    if not line or line.startswith('#'):
        continue
    
    parts = line.split(':')
    replaced_poks[parts[0]] = parts[1]

with open(FORMS_FILE, 'r') as file:
    forms_lines = file.readlines()

forms = {}
reversed_forms = {}
other_formes = {}
for line in forms_lines:
    line = line.strip()
    
    if not line or line.startswith('#'):
        continue
    
    parts = line.split(':')
    forms[parts[0]] = parts[1]
    reversed_forms[parts[1]] = parts[0].split(' ')[0]
    
    pok = parts[0].split(' ')[0]
    if not pok in other_formes:
        other_formes[pok] = []
    other_formes[pok].append(parts[1])

with open(POKS_FILE, 'r', encoding = 'utf-16') as file:
    poks_lines = file.readlines()

poks_data = {}
for i, line in enumerate(poks_lines):
    line = line.strip()
    
    if not line:
        continue
    
    if line[0].isnumeric() and line[0] != '0':
        current_pok = line.split(' - ')[1]
        
        bs = None
        abilities = None
        types = None
        weightkg = None
            
        j = 2
        while i + j < len(poks_lines):
            subline = poks_lines[i + j].strip()

            if not subline or subline.startswith('='):
                break
            
            if subline.startswith('Base Stats:'):
                pid = int(line.split(' - ')[0])
                
                stats = subline.split(' ')[2].split('.')
                bs = {
                    'hp': int(stats[0]),
                    'at': int(stats[1]),
                    'df': int(stats[2]),
                    'sa': int(stats[3]),
                    'sd': int(stats[4]),
                    'sp': int(stats[5]),
                }
                
            if subline.startswith('Abilities:'):
                abils = subline.replace('Abilities: ', '').split(' | ')
                abilities = [
                    abils[0][:-4],
                    abils[1][:-4],
                    abils[2][:-4],
                ]
            
            if subline.startswith('Type:'):
                ts = subline.replace('Type: ', '').split(' / ')
                types = [
                    ts[0],
                ]
                
                if '/' in subline:
                    types.append(ts[1])
            
            if subline.startswith('Height:'):
                weightkg = float(subline.split(', ')[1].replace('Weight: ', '').replace(' kg', ''))
            
            j += 1

        if any([
            bs is None,
            abilities is None,
            types is None,
            weightkg is None
        ]):
            print(f'===\nUnable to gather data for: {current_pok}')
            print(f'bs: {bs}')
            print(f'abilities: {abilities}')
            print(f'types: {types}')
            print(f'weightkg: {weightkg}')
            print('===\n')
            
            continue
            
        pok_data = {
            'bs'        : bs,
            'abilities' : abilities,
            'types'     : types,
            'weightkg'  : weightkg,
            'id'        : pid,
        }
        
        base_species = None
        if current_pok in forms:
            current_pok = forms[current_pok]
            base_species = reversed_forms[current_pok]
        
        if base_species is not None:
            pok_data['baseSpecies'] = base_species
        
        if current_pok in other_formes:
            pok_data['otherFormes'] = other_formes[current_pok]
            
        poks_data[current_pok] = pok_data
        
        if current_pok in replaced_poks:
            poks_data[replaced_poks[current_pok]] = pok_data
#endregion Poks Data

#region Learnset Data
with open(LEVELUP_FILE, 'r', encoding = 'utf-16') as file:
    levelup_lines = file.readlines()

for i, line in enumerate(levelup_lines):
    line = line.strip()
    
    if not line:
        continue
    
    if line[0].isnumeric() and not '-' in line and line[0] != '0':
        current_pok = line[line.find(' ') + 1:]

        if not current_pok in poks_data and not current_pok in forms:
            print(f'Levelup moves found for {current_pok}, but pok not in poks_data.')

            continue
        
        if current_pok in forms:
            current_pok = forms[current_pok]
        
        j = 2
        levelup_moves = []
        while i + j < len(levelup_lines):
            subline = levelup_lines[i + j].strip()

            if not subline:
                break
            
            data = subline.split(' - ')
            move = [
                int(data[0]),
                data[1]
            ]

            levelup_moves.append(move)

            j += 1

        poks_data[current_pok]['learnset_info'] = levelup_moves
#endregion Learnset Data
    
#region Trainer Data
with open(TRAINERS_FILE, 'r', encoding = 'utf-8') as file:
    trainers_lines = file.readlines()

ABILITY_INDICES = {
    'Stench'        : 0,
    'Drizzle'       : 1,
    'Speed Boost'   : 2,
}

trainers_data = {}
repeat_trainers = {}
for i, line in enumerate(trainers_lines):
    line = line.strip()
    
    if not line:
        continue
    
    if line[0].isnumeric() and line[0] != '0' and '-' in line and not '[' in line and not '●' in line:
        current_trainer = line.split(' - ')[1]

        if not current_trainer in repeat_trainers:
            repeat_trainers[current_trainer] = 0
        repeat_trainers[current_trainer] += 1

        num_poks = int(trainers_lines[i + 1][:-1])
        
        for n in range(num_poks):
            base = i + 2 + n * 9
            
            pok = trainers_lines[base].strip()
            
            if not pok in poks_data:
                print(f'Set found for {pok}, but pok not in poks_data.')
            
            level = int(trainers_lines[base + 1])
            
            item = trainers_lines[base + 2].strip()
            if item == '(None)':
                item = None
                
            nature = trainers_lines[base + 3].strip()
            
            ability = trainers_lines[base + 4].strip()
            ability_slot = ABILITY_INDICES.get(ability)
            
            if ability_slot is not None:
                ability = poks_data[pok]['abilities'][ability_slot]
            
            moves = [move for move in trainers_lines[base + 5].strip().split(' / ')]
            ivs = dict(zip(
                ('hp', 'at', 'df', 'sa', 'sd', 'sp'),
                map(int, trainers_lines[base + 6].split('/'))
            ))
            evs = dict(zip(
                ('hp', 'at', 'df', 'sa', 'sd', 'sp'),
                map(int, trainers_lines[base + 7].split('/'))
            ))
        
            if not pok in trainers_data:
                trainers_data[pok] = {}
            
            trainers_data[pok][f'Lvl {level} {current_trainer} {repeat_trainers[current_trainer]} '] = {
                'evs'       : evs,
                'ivs'       : ivs,
                'level'     : level,
                'nature'    : nature,
                'item'      : item,
                'moves'     : moves,
                'ability'   : ability,
                'sub_index' : n,
            }
#endregion Trainer Data
    
data = {
    'title'             : GAME_TITLE,
    'moves'             : moves_data,
    'poks'              : poks_data,
    'formatted_sets'    : trainers_data,
}

#if replaced_poks:
#    data['poks_replacements'] = replaced_poks

with open(OUTPUT_FILE, 'w') as file:
    json.dump(data, file, indent = 4)
