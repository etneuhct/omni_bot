import discord
from discord.ext import commands
from bot.omni_bot import OmniBot
from pokemon.pokemon import *
from pokemon.space import *

atts = [ActionNames.ATT1, ActionNames.ATT2, ActionNames.ATT3, ActionNames.ATT4]
input_to_action = {str(atts.index(att) + 1): att for att in atts}


class PokemonDialog:
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


class CommandPokemon(commands.Cog, name='Pokemon'):

    def __init__(self, bot: OmniBot):
        self.bot = bot
        self.temp = {}

    @commands.command(name="pkmn_info", help=PokemonDialog.GLOBALINFO)
    async def search_participant(self, ctx):
        message = PokemonDialog.CREATEMATCHMESSAGE
        channel = ctx.channel
        await channel.send(message)

    @commands.command(name="pkmn_s", help=PokemonDialog.HELPGAMESUBSCRIPTION)
    async def game_subscription(self, ctx, pokemon: str):
        guild_id = ctx.guild.id
        if guild_id not in self.bot.storage['pokemon']:
            self.bot.storage['pokemon'][guild_id] = {}
        guild = self.bot.storage['pokemon'][guild_id]
        if 'participants' not in guild:
            guild['participants'] = []
            guild['actions'] = {}
        pokemon = pokemon.strip().split(',')
        if len(guild['participants']) < 2 \
                and ctx.message.author.id not in [player.user_id for player in guild['participants']]:
            pokemon = [Pokemon(**get_pokemon(pId.strip())) for pId in pokemon]
            player = Player(ctx.message.author.id, ctx.message.author.name, pokemon)
            guild['participants'].append(player)
            await ctx.channel.send(PokemonDialog.SUBSCRIPTIONRECORDED)
        if len(guild['participants']) == 2:
            await ctx.channel.send(PokemonDialog.ENOUGHPARTICIPANT.format(guild['participants'][0].name,
                                                                          guild['participants'][1].name))
            players = self.bot.storage['pokemon'][guild_id]['participants']
            match = Match(player1=players[0], player2=players[1])
            match.start()
            self.bot.storage['pokemon'][guild_id]['match'] = match
            await ctx.channel.send(PokemonDialog.STARTMATCH)

    @commands.command(name="pkmn_f", help=PokemonDialog.HELPFIGHT)
    async def attack(self, ctx, action: str):
        try:
            guild_id = ctx.guild.id
            guild = self.bot.storage['pokemon'][guild_id]
        except KeyError as e:
            print(str(e))
            return

        if get_player_by_id(guild['participants'], ctx.message.author.id) and action in [str(i) for i in
                                                                                         range(1, 5)]:
            if 'actions' not in guild:
                guild['actions'] = {}
            guild['actions'][ctx.message.author.id] = input_to_action[action]
            await ctx.channel.send(PokemonDialog.ACTIONREGISTER)
        if len(guild['actions']) == 2:
            match: Match = guild['match']
            p1_action = guild['actions'][match.player1.user_id]
            p2_action = guild['actions'][match.player2.user_id]
            result = match.fight(p1_action, p2_action)
            await ctx.channel.send('Fight !')
            await ctx.channel.send(result)
            guild['actions'] = {}
            if match.status == MatchStatus.FINISHED:
                self.bot.storage['pokemon'][guild_id] = {}
            return
        else:
            return

        # await ctx.channel.send(PokemonDialog.GLOBALATTAKERROR)

    @commands.command(name='pkmn_whois', help=PokemonDialog.HELPPOKEMONINFO)
    async def pokemon_info(self, ctx, pokemon: str = None):
        pokemon_dict = get_pokemon_list()
        if not pokemon:
            message = discord.Embed(title='Pokemon', type='rich')
            for key in pokemon_dict:
                pokemonObj: Pokemon = pokemon_dict[key]
                value = "Attaques:\n* " + "\n* ".join([pokemonObj.actions[action_key].name for action_key in pokemonObj.actions])
                message.add_field(name=key, value=value, inline=True)
            await ctx.channel.send(embed=message)
        else:
            try:
                pokemonObj: Pokemon = pokemon_dict[pokemon]
                pokemon_type = get_pokemon_typ(pokemonObj)
                message = discord.Embed(title=pokemonObj.name, type='rich')
                message.add_field(name="Type", inline=False, value=pokemon_type)
                message.add_field(name="Attaques", value="* " + "\n* ".join([pokemonObj.actions[action_key].name for action_key in pokemonObj.actions]))
                message.add_field(name="Stats", value=pokemonObj.get_stat_info())
                if pokemonObj.img:
                    message.set_thumbnail(url=pokemonObj.img)
                await ctx.channel.send(embed=message)
            except KeyError:
                await ctx.channel.send("Ce pokemon n'existe pas !")

    @commands.command(name='pkmn_whoiam', help='Nope')
    async def get_user_info(self, ctx, user_id=None):
        try:
            searched_user = user_id if user_id else ctx.message.author.id
            players = self.bot.storage['pokemon'][ctx.guild.id]['participants']
            player: Player = get_player_by_id(players, searched_user)
            if player:
                embed = discord.Embed(title=player.name, type='rich', description="Liste des pokemon du joueur")
                for pokemon in player.pokemon:
                    att = "* " + "\n* ".join(
                        [pokemon.actions[action_key].name for action_key in pokemon.actions])
                    pokemon_type = get_pokemon_typ(pokemon)
                    embed.add_field(name='Pokemon', value='Nom: {}\nType: {}'.format(pokemon.name, pokemon_type), inline=True)
                    embed.add_field(name='Attaques', value=att, inline=True)
                    embed.add_field(name='Stats', value=pokemon.get_stat_actual_info(), inline=True)
                await ctx.channel.send(embed=embed)
        except KeyError:
            return


def get_player_by_id(players, user_id):
    for player in players:
        if player.user_id == user_id:
            return player
    return None


def get_pokemon_typ(pokemonObj: Pokemon):
    pokemon_type = pokemonObj.type1
    if pokemonObj.type2:
        pokemon_type = pokemon_type + " | " + pokemonObj.type2
    return pokemon_type

