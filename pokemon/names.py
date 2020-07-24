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


class PokemonDialog:
    PLAYERS = "Donne les info des joueurs"
    WHOIAM = "Donne les info du joueur"
    HELPACTIVEPOKEMON = "Liste des pokemon actifs"
    HELPPLAYERINFO = "Info sur les joueurs"
    HELPPOKEMONINFO = "Info sur les pokemon dispo"
    ACTIONREGISTER = 'Enregistrement complété avec succès'
    HELPFIGHT = "Utilise un chiffre compris entre 1 et 4 pour choisir l'attaque a executer"
    GLOBALATTAKERROR = 'Impossible !'
    STARTMATCH = 'Let the game begin !'
    SUBSCRIPTIONRECORDED = 'Enregistrement complété avec succès'
    HELPGAMESUBSCRIPTION = 'Inscris toi en renseignant les pokemon que tu veux utiliser'
    ENOUGHPARTICIPANT = 'Participants:\nJoueur 1: {}\nJoueur 2: {}'
    NOTENOUGHPARTICIPANT = "2 participants doivent se battre"
    GLOBALINFO = "Jouons à pokemon !"
    CREATEMATCHMESSAGE = "R.A.S"
