class PokemonType:
    ELECTRIC = "electric"


class PokemonStat:
    SPEED = 'speed'
    PV = 'hp'
    ATT, DEF, ATTSPE, DEFSPE = 'attack', 'defense', 'special_attack', 'special_defense'


class ActionNames:
    ATT1, ATT2, ATT3, ATT4 = ['capacity{}'.format(i) for i in range(1, 5)]


class ActionEffect:
    DECREASEDEF = 'decrease_def'
    DECREASEDEFSPE = 'decrease_def_spe'
    DECREASEVIT = 'decrease_vit'
    DECREASEATT = 'decrease_att'
    DECREASEATTSPE = 'decrease_att_spe'
    HEAL = 'heal'
    INFLICTDMG = 'inflict_dmg'


class ActionCategory:
    SPECIAL, PHYSIC = 'special', 'physical'


class MatchStatus:
    FINISHED = 'finished'
    PROGRESSING, WAITING = 'progressing', 'waiting'