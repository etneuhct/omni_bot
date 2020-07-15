from utils import utils
import random


class Pendu:
    mot = ""
    motCachay = ""
    bonhomme = ['''```
                       ______
                       |    |
                       O    |
                      -|-   |
                      / \   |
                        _________```''', '''```
                       ______
                       |    |
                       O    |
                      -|-   |
                      /     |
                        _________```''', '''```
                       ______
                       |    |
                       O    |
                      -|-   |
                            |
                        _________```''', '''```
                       ______
                       |    |
                       O    |
                      -|    |
                            |
                        _________```''', '''```
                       ______
                       |    |
                       O    |
                       |    |
                            |
                        _________```''', '''```
                       ______
                       |    |
                       O    |
                            |
                            |
                        _________```''', '''```
                       ______
                       |    |
                            |
                            |
                            |
                        _________```''', '''```
                       ______
                            |
                            |
                            |
                            |
                        _________```''', '''```       
                            |
                            |
                            |
                            |
                        _________```''', '```___________```', '']

    def __init__(self, nombre_coup: int = 10, minimum_letter=8, maximum_letter=20, language='fr'):
        words = utils.get_dictionary_word(minimum_letter, maximum_letter, language)
        word = random.choice(words)
        word = utils.message_transformation(word)
        self.mot = word
        self.lettreDejaUse = []
        self.nombreCoup = nombre_coup
        for i in range(len(self.mot)):
            self.motCachay += "_"


    def checkLettre(self, lettre):
        """
        Retour de checkLettre : 0 c'est pas la bonne lettre, 1 c'est la bonne, -1 c'est deja test.
        Si la lettre qu'on test n'est pas dans la liste des lettres testees, alors on check la lettre normalement pour éviter de
        perdre des pv inutilement si on check la meme lettre plusieurs fois.
        :param lettre:
        :return:
        """
        bonneLettre = False
        motCachayList = list(self.motCachay)
        if lettre not in self.lettreDejaUse:
            for i in range(len(self.mot)):
                if lettre == self.mot[i]:
                    motCachayList[i] = lettre
                    bonneLettre = True

            if bonneLettre == False:
                self.nombreCoup -= 1
            self.motCachay = "".join(motCachayList)
            self.lettreDejaUse.append(lettre)
            return bonneLettre
        return -1

    def getMot(self):
        return "```{}```".format(" ".join(list(self.motCachay)))

    def getCoupRestant(self):
        return self.nombreCoup

    def getBonhomme(self):
        return self.bonhomme[self.nombreCoup]

    def getLettre(self):
        return self.lettreDejaUse
