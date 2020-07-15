import settings
import os
import csv

def get_data():
    folder = os.path.join(settings.INPUT_PATH, 'pokemon')
    pokemon_file = os.path.join(folder, 'pokemon.csv')
    pokemon_att_file = os.path.join(folder, 'pokemonAtt.csv')
    type_table_file = os.path.join(folder, 'type_table.csv')

    stats_name = ['att', 'def', 'def_spe', 'att_spe', 'speed', 'pv']
    actions_name = ['att1', 'att2', 'att3', 'att4']

    pokemon_actions = {}
    with open(pokemon_att_file) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            data = dict(row)
            data['precision'] = int(data['precision'])
            data['value'] = int(data['value'])
            pokemon_actions[data['id']] = data

    pokemon = {}
    with open(pokemon_file) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            data = dict(row)
            result = {
                'name': data['name'],
                'stats': {stat: data[stat] for stat in stats_name},
                'actions': {action: pokemon_actions[data[action]] if data[action] in pokemon_actions else None for action in actions_name},
                'type1': data['type1'], 'type2': data['type2'],
                'img': data['img']
            }
            pokemon[data['name']] = result

    table_type = {}
    with open(type_table_file) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            data = dict(row)
            name = "".join([data['att'], data['def']])
            table_type[name] = float(data['coefficient'])

    return pokemon, table_type