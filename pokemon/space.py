class PokemonType:
    ELECTRIC = "electric"


class PokemonStat:
    SPEED = 'speed'
    PV = 'pv'
    ATT, DEF, ATTSPE, DEFSPE = 'att', 'def', 'att_spe', 'def_spe'


class ActionNames:
    ATT1, ATT2, ATT3, ATT4 = ['att{}'.format(i) for i in range(1, 5)]


class ActionEffect:
    DECREASEDEF = 'decrease_def'
    DECREASEDEFSPE = 'decrease_def_spe'
    DECREASEVIT = 'decrease_vit'
    DECREASEATT = 'decrease_att'
    DECREASEATTSPE = 'decrease_att_spe'
    HEAL = 'heal'
    INFLICTDMG = 'inflict_dmg'


class ActionCategory:
    SPECIAL, PHYSIC = 'spe', 'physic'


class MatchStatus:
    FINISHED = 'finished'
    PROGRESSING, WAITING = 'progressing', 'waiting'