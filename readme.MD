# omni_bot

Ce programme permet de lancer un bot Discord. Ce bot offre la possiblité de jouer au Pendu et à une version pour le moins artisanale du jeu Pokemon !
Il permet également de renvoyer une liste de messages supprimés par d'autres utilisateur du serveur Discord.

## Premiers pas
a) Récupérer le dépôt
```bash
git clone https://github.com/etneuhct/omni_bot.git
```
```bash
cd omni_bot
```

b) Installer les dépendances
```bash
pip install -r requirements.txt
```

c) Configurer le projet
```bash
python manage.py migrate
python pokemon/populate.py
```

d) Démarrer le serveur
```bash
python main.py
```
