import custom_settings
import requests
from pokemon.models import Pokemon, PokemonType, PokemonCapacity, DamageEffect, HealEffect, StatEffect
first_pkmn = 1
last_pkmn = 300
first_att = 1
last_att = 100
type_base_request_url = "https://pokeapi.co/api/v2/type/"
type_name = {}

for i in range(1, 19):
    request = requests.get(type_base_request_url + str(i)).json()
    en_name = request["name"]
    fr_name = request["names"][2]["name"]
    type_name[en_name] = fr_name

for pokemon_type in type_name:
    PokemonType.objects.get_or_create(name=type_name[pokemon_type])

pokemon_species_base_request_url = "https://pokeapi.co/api/v2/pokemon-species/"
pokemon_name = {}
for i in range(first_pkmn, last_pkmn):
    request = requests.get(pokemon_species_base_request_url + str(i)).json()
    en_name = request["name"]
    fr_name = request["names"][4]["name"]
    pokemon_name[en_name] = fr_name

pokemon_list = []

pokemon_base_request_url = "https://pokeapi.co/api/v2/pokemon/"
for i in range(first_pkmn, last_pkmn):
    request = requests.get(pokemon_base_request_url+str(i)).json()
    name = pokemon_name[request['name']]
    url = request['forms'][0]['url']
    pokemon_form = requests.get(url).json()
    image = pokemon_form['sprites']['front_default']
    types = [type_name[element["type"]["name"]] for element in request['types']]
    pokemon_id = request["id"]
    stats = {stat["stat"]['name'].replace("-", "_"): stat["base_stat"] for stat in request["stats"]}
    pokemon = {"name": name, "image": image, "types": types, "stats": stats}
    pokemon_list.append(pokemon)

for pokemon in pokemon_list:
    data = {
        "type_1": PokemonType.objects.get(name=pokemon["types"][0]),
        "type_2": PokemonType.objects.get(name=pokemon["types"][1]) if len(pokemon["types"]) == 2 else None,
        "picture_url": pokemon["image"],
        "name": pokemon["name"],
        **pokemon["stats"]
    }
    Pokemon.objects.get_or_create(
        **data
    )

move_base_request_url = "https://pokeapi.co/api/v2/move/"
for i in range(first_att, last_att):
    request = requests.get(move_base_request_url + str(i)).json()
    att_name = request["names"][3]["name"]
    power = request["power"]
    power_point = request["pp"]
    att_type = type_name[request["type"]["name"]]
    accuracy = request["accuracy"] if request["accuracy"] else 100
    att_category = request["damage_class"]["name"]
    heal = request['meta']["healing"]
    damage_effect = DamageEffect.objects.create(damage=power) if power and power > 0 else None
    heal_effect = HealEffect.objects.create(healing=heal) if heal and heal > 0 else None
    PokemonCapacity.objects.get_or_create(
        name=att_name, power_point=power_point, precision=accuracy, damage_effect=damage_effect,
        heal_effect=heal_effect, category=att_category, capacity_type=PokemonType.objects.get(name__iexact=att_type)
    )



