import random
from pokemon.db import get_data
from pokemon.space import *

db = get_data()
pkmns = db[0]
table_type = db[1]

stat_value = ['Attaque', 'Defense', 'Defense Speciale', 'Attaque Speciale', 'Vitesse', 'Point de vie']
stat_key = ['att', 'def', 'def_spe', 'att_spe', 'speed', 'pv']
stat_data = {key: stat_value[stat_key.index(key)] for key in stat_key}


class Action:

    def __init__(self, id, name, type, effect, precision, value, category):
        self.name, self.type, self.effect, self.precision, self.value, self.category, self.id \
            = name, type, effect, precision, value, category, id

    def get_info(self):
        return "* Nom {}, Precision: {}, Type: {}".format(self.name, self.precision, self.type)


class Pokemon:

    def __init__(self, name, stats, actions, type1, type2, img):
        self.img = img
        self.name = name
        self.level = 30
        self.actions = {
            action: Action(**actions[action])
            for action in actions
        }
        init_stat = {stat: int(stats[stat]) for stat in stats}
        self.stats = {**init_stat}
        self.initial_stat = {**init_stat}
        self.type1, self.type2 = type1.strip(), type2.strip()

    def act(self, action_id, opponent):
        action = self.actions[action_id]
        if action:
            miss = 100 - action.precision
            hit = random.choice([False for _ in range(miss)] + [True for _ in range(action.precision)])
            message = "{} lance {}".format(self.name, action.name)
            if hit:
                if action.effect == ActionEffect.INFLICTDMG:
                    message = self.inflict_dmg(action, message, opponent)
                elif action.effect == ActionEffect.HEAL:
                    self.increase_stat(PokemonStat.PV, action.value)
                    self.heal(action.value)
                    message = "{}. {} regagne {} pv".format(message, self.name, action.value)
                elif 'decrease' in action.effect:
                    stat = action.effect.replace("decrease_", "")
                    opponent.decrease_stat(stat, action.value)
                    message = message + ". {} en baisse".format(stat)
                elif 'increase' in action.effect:
                    stat = action.effect.replace("increase_", "")
                    self.increase_stat(stat, action.value)
                    message = message + ". {} en hausse".format(stat)
            else:
                message = message + ". Mais cela échoue."
            return message

    def decrease_pv(self, value):
        self.stats[PokemonStat.PV] -= value
        if self.stats[PokemonStat.PV] < 0:
            self.stats[PokemonStat.PV] = 0
        self.stats[PokemonStat.PV] = int(self.stats[PokemonStat.PV])

    def receive_dmg(self, value, att_type, category):
        power_coefficient = 1
        type_coefficient = 1.0
        if category == ActionCategory.SPECIAL:
            used_stat = self.stats[PokemonStat.ATTSPE]
        else:
            used_stat = self.stats[PokemonStat.ATT]
        power_coefficient += used_stat / 100

        if self.type1:
            rapport1 = att_type + self.type1
            type_coefficient = table_type[rapport1] * type_coefficient
        if self.type2:
            rapport2 = att_type + self.type2
            type_coefficient = table_type[rapport2] * type_coefficient
        damage = value * power_coefficient * type_coefficient
        return damage

    def get_stab(self, att_type):
        type_coefficient = 1
        rapport1 = att_type + self.type1
        type_coefficient = table_type[rapport1] * type_coefficient
        if self.type2:
            rapport2 = att_type + self.type2
            type_coefficient = table_type[rapport2] * type_coefficient
        return type_coefficient

    def inflict_dmg(self, action, message, opponent):
        if action.category == ActionCategory.SPECIAL:
            att = self.stats[PokemonStat.ATT]
            defense = self.stats[PokemonStat.DEF]
        else:
            att = self.stats[PokemonStat.ATTSPE]
            defense = self.stats[PokemonStat.DEFSPE]
        CM = opponent.get_stab(action.type)
        received_damage = (((self.level * att * action.value) / (defense * 50)) + 2) * CM
        opponent.decrease_pv(received_damage)
        message = "{}. {} subit {} dommages.".format(message, opponent.name, received_damage)
        if opponent.stats[PokemonStat.PV] <= 0:
            message = message + "\n{} est K.O.".format(opponent.name)
        return message

    def heal(self, value):
        self.stats[PokemonStat.PV] += self.initial_stat[PokemonStat.PV] * value / 100
        self.stats[PokemonStat.PV] = int(self.stats[PokemonStat.PV])
        if self.stats[PokemonStat.PV] > self.initial_stat[PokemonStat.PV]:
            self.stats[PokemonStat.PV] = self.initial_stat[PokemonStat.PV]

    def decrease_stat(self, stat_name, value):
        self.stats[stat_name] -= value
        if self.initial_stat[stat_name] - self.stats[stat_name] > 60:
            self.stats[stat_name] = self.initial_stat[stat_name] - 60
        if self.stats[stat_name] < 0:
            self.stats[stat_name] = 0

    def increase_stat(self, stat_name, value):
        self.stats[stat_name] += value
        if self.stats[stat_name] - self.initial_stat[stat_name] > 60:
            self.stats[stat_name] = self.initial_stat[stat_name] + 60

    def get_info(self):
        stats_info = " | ".join(["{} : {} -> {}".format(stat, self.initial_stat[stat], self.stats[stat])
                                 for stat in ['att', 'def', 'def_spe', 'att_spe', 'speed', 'pv']])
        return "Nom: {}, Type1: {}, Type2: {}, \nAttaques\n{}\n{}" \
            .format(self.name, self.type1, self.type2,
                    "\n".join([self.actions[key].get_info() for key in self.actions]), stats_info)

    def get_stat_info(self):
        return "* " + "\n* ".join(["{} : {}".format(stat_data[stat], self.initial_stat[stat])
                                   for stat in ['att', 'def', 'def_spe', 'att_spe', 'speed', 'pv']])

    def get_stat_actual_info(self):
        return "* " + "\n* ".join(["{} : {} -> {}".format(stat_data[stat], self.initial_stat[stat], self.stats[stat])
                                   for stat in ['att', 'def', 'def_spe', 'att_spe', 'speed', 'pv']])


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
            player1_pokemon = self.get_active_pokemon(self.player1)
        except IndexError as e:
            return "{} n'a plus de pokemon prêts à se battre. Le combat est fini".format(self.player1.name)
        try:
            player2_pokemon = self.get_active_pokemon(self.player2)
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
            self.get_active_pokemon(self.player1)
        except IndexError as e:
            result = result + "{} n'a plus de pokemon prêts à se battre. Le combat est fini".format(self.player1.name)
            self.end()
        try:
            self.get_active_pokemon(self.player2)
        except IndexError as e:
            result = result + "{} n'a plus de pokemon prêts à se battre. Le combat est fini".format(self.player2.name)
            self.end()

        return result

    @staticmethod
    def get_active_pokemon(player: Player):
        return [pokemon for pokemon in player.pokemon if pokemon.stats[PokemonStat.PV] > 0][0]

    @staticmethod
    def get_fastest_pokemon(pokemon1: Pokemon, pokemon2: Pokemon):
        if pokemon1.stats[PokemonStat.SPEED] > pokemon2.stats[PokemonStat.SPEED]:
            return 0
        elif pokemon1.stats[PokemonStat.SPEED] < pokemon2.stats[PokemonStat.SPEED]:
            return 1
        else:
            return random.choice([0, 1])

    def get_info(self):
        return "{}\n\n{}".format(self.player1.get_info(), self.player2.get_info())


def get_pokemon(pokemon_id):
    return pkmns[pokemon_id]


def get_pokemon_list():
    return {key: Pokemon(**pkmns[key]) for key in pkmns}  # ",".join(list(pkmns.keys()))


"""p1 = Player('j1', pokemon=[Pokemon(**pkmns['pikachu']), Pokemon(**pkmns['pikachu'])])
p2 = Player('j2', pokemon=[Pokemon(**pkmns['pikachu']), Pokemon(**pkmns['pikachu'])])
match = Match(p1, p2)
match.start()
match.fight(ActionNames.ATT4, ActionNames.ATT3)
match.fight(ActionNames.ATT4, ActionNames.ATT3)
print(match.get_info())
"""
"""
pktype = "Normal, Fighting, Flying, Poison, Ground, Rock, Bug, Ghost, Steel, Fire, Grass, Water, Electric, Psychic, Ice, Dragon, Dark, Fairy"
p = sorted(pktype.replace(' ', '').lower().split(','))
for i in p:
    for j in p:
        print("{};{}".format(i, j))"""

