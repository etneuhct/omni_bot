import custom_settings
import random
from django.db.models import Q
from django.forms import model_to_dict
from pokemon.models import Pokemon, PokemonCapacity, PokemonType, TypeEfficacity
from pokemon.names import PokemonStat, ActionCategory, MatchStatus


class CapacityDex:

    def __init__(self):
        pokemon_capacities = PokemonCapacity.objects \
            .filter(Q(damage_effect__isnull=False) | Q(heal_effect__isnull=False))
        self.all_capacities = {}
        for pokemon_capacity in pokemon_capacities:
            self.all_capacities[pokemon_capacity.name] = model_to_dict(pokemon_capacity)


class CapacityObj:

    def __init__(self, pokemon_capacity: PokemonCapacity):
        self.damage_effect = pokemon_capacity.damage_effect
        self.name = pokemon_capacity.name
        self.precision = pokemon_capacity.precision
        self.category = pokemon_capacity.category
        self.capacity_type = pokemon_capacity.capacity_type


class Pokedex:

    def __init__(self):
        self.all_pokemon = {}
        self.used_stats = ["hp", "attack", "special_attack", "special_defense", "defense", "speed"]
        for pokemon in Pokemon.objects.all().filter(capacity1__isnull=False,
                                                    capacity4__isnull=False,
                                                    capacity3__isnull=False,
                                                    capacity2__isnull=False):
            pokemon_dict = model_to_dict(pokemon)
            stats = {stat: pokemon_dict[stat] for stat in self.used_stats}
            pokemonObj = PokemonObj(name=pokemon.name, picture_url=pokemon.picture_url,
                                    capacities={capacity: pokemon_dict[capacity]
                                                for capacity in ["capacity1", "capacity2", "capacity3", "capacity4"]},
                                    type1=pokemon.type_1, type2=pokemon.type_2, stats=stats)
            self.all_pokemon[pokemon.name] = pokemonObj

    def get_pokemon(self, pokemon_name):
        try:
            pokemon = Pokemon.objects.get(name=pokemon_name)
            pokemon_dict = model_to_dict(pokemon)
            stats = {stat: pokemon_dict[stat] for stat in self.used_stats}
            return PokemonObj(name=pokemon.name, picture_url=pokemon.picture_url,
                              capacities={
                                            "capacity1": CapacityObj(pokemon.capacity1),
                                            "capacity2": CapacityObj(pokemon.capacity2),
                                            "capacity3": CapacityObj(pokemon.capacity3),
                                            "capacity4": CapacityObj(pokemon.capacity4)
                                          },
                              type1=pokemon.type_1, type2=pokemon.type_2, stats=stats)
        except Pokemon.DoesNotExist:
            return


class PokemonObj:

    def __init__(self, name, stats, capacities, type1, type2, picture_url):
        self.picture_url = picture_url
        self.name = name
        self.capacities = capacities
        self.level = 30
        self.stats = {**stats}
        self.initial_stats = {**stats}
        self.type1, self.type2 = type1, type2

    def decrease_pv(self, value):
        self.stats[PokemonStat.PV] -= value
        if self.stats[PokemonStat.PV] < 0:
            self.stats[PokemonStat.PV] = 0
        self.stats[PokemonStat.PV] = int(self.stats[PokemonStat.PV])

    def receive_dmg(self, value, att_type, category):
        power_coefficient = 1
        type_coefficient = self.get_stab(att_type)
        if category == ActionCategory.SPECIAL:
            used_stat = self.stats[PokemonStat.ATTSPE]
        else:
            used_stat = self.stats[PokemonStat.ATT]
        power_coefficient += used_stat / 100
        damage = value * power_coefficient * type_coefficient
        return damage

    def inflict_dmg(self, action: CapacityObj, message, opponent):
        if action.category == ActionCategory.PHYSIC:
            att = self.stats[PokemonStat.ATT]
            defense = self.stats[PokemonStat.DEF]
        else:
            att = self.stats[PokemonStat.ATTSPE]
            defense = self.stats[PokemonStat.DEFSPE]
        CM = opponent.get_stab(action.capacity_type)
        received_damage = (((self.level * att * action.damage_effect.damage) / (defense * 50)) + 2) * CM
        opponent.decrease_pv(received_damage)
        efficacy_message = "C'est super efficace. " if CM > 1 else "Ce n'est pas très efficace. " if CM < 1 else ""
        message = "{} {}{} subit {} dommages.".format(message, efficacy_message, opponent.name, received_damage)
        if opponent.stats[PokemonStat.PV] <= 0:
            message = message + "\n{} est K.O.".format(opponent.name)
        return message

    def get_stab(self, att_type):
        type_coefficient = 1
        type_coefficient = TypeEfficacity.objects.get(attack_type=PokemonType.objects.get(name=att_type),
                                                      defense_type=PokemonType.objects.get(
                                                          name=self.type1)).coefficient * type_coefficient
        if self.type2:
            type_coefficient = TypeEfficacity.objects.get(
                attack_type=PokemonType.objects.get(name=att_type),
                defense_type=PokemonType.objects.get(name=self.type2)).coefficient * type_coefficient
        return type_coefficient

    def act(self, action_id, opponent):
        action: CapacityObj = self.capacities[action_id]
        if action:
            miss = 100 - action.precision
            hit = random.choice([False for _ in range(miss)] + [True for _ in range(action.precision)])
            message = "{} lance {}.".format(self.name, action.name)
            if hit:
                if action.damage_effect:
                    message = self.inflict_dmg(action, message, opponent)
            else:
                message = message + "Mais cela échoue."
            return message


class Player:

    def __init__(self, user_id, name, pokemon):
        self.user_id = user_id
        self.name = name
        self.pokemon = pokemon

    def get_info(self):
        info = "Nom: {}" \
               "\n\nPokemon ({}/{})" \
               "\n{}".format(self.name, len([pokemon for pokemon in self.pokemon if pokemon.stats[PokemonStat.PV] > 0]),
                             len(self.pokemon), '\n- '.join(["\n{pokemon_info}".format(pokemon_info=pokemon.get_info())
                                                             for pokemon in self.pokemon]))
        return info

    def get_active_pokemon(self):
        return [pokemon for pokemon in self.pokemon if pokemon.stats[PokemonStat.PV] > 0][0]


class Match:

    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.status = MatchStatus.WAITING
        self.round = 0

    def start(self):
        self.status = MatchStatus.PROGRESSING

    def end(self):
        self.status = MatchStatus.FINISHED

    def fight(self, player1_action, player2_action):
        done = False
        try:
            player1_pokemon = self.player1.get_active_pokemon()
        except IndexError as e:
            return "{} n'a plus de pokemon prêts à se battre. Le combat est fini".format(self.player1.name)
        try:
            player2_pokemon = self.player2.get_active_pokemon()
        except IndexError as e:
            return "{} n'a plus de pokemon prêts à se battre. Le combat est fini".format(self.player2.name)
        fastest = self.get_fastest_pokemon(player1_pokemon, player2_pokemon)
        if fastest == 0:
            opponents = [(player1_pokemon, player1_action, self.player1.name),
                         (player2_pokemon, player2_action, self.player2.name)]
        else:
            opponents = [(player2_pokemon, player2_action, self.player2.name),
                         (player1_pokemon, player1_action, self.player1.name)]

        self.round += 1
        result = "Tour : {}\n".format(self.round)
        for opponent in opponents:
            if opponent[0].stats[PokemonStat.PV] > 0 and not done:
                index = opponents.index(opponent)
                opponent_index = index - 1
                action = opponent[0].act(opponent[1], opponents[opponent_index][0])
                result = result + 'Joueur: {}\n'.format(opponent[2]) + action + '\n'
            else:
                done = True
        try:
            self.player1.get_active_pokemon()
        except IndexError as e:
            result = result + "{} n'a plus de pokemon prêts à se battre. Le combat est fini".format(self.player1.name)
            self.end()
        try:
            self.player2.get_active_pokemon()
        except IndexError as e:
            result = result + "{} n'a plus de pokemon prêts à se battre. Le combat est fini".format(self.player2.name)
            self.end()

        return result

    @staticmethod
    def get_fastest_pokemon(pokemon1: PokemonObj, pokemon2: PokemonObj):
        if pokemon1.stats[PokemonStat.SPEED] > pokemon2.stats[PokemonStat.SPEED]:
            return 0
        elif pokemon1.stats[PokemonStat.SPEED] < pokemon2.stats[PokemonStat.SPEED]:
            return 1
        else:
            return random.choice([0, 1])

    def get_info(self):
        return "{}\n\n{}".format(self.player1.get_info(), self.player2.get_info())
