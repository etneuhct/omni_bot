from asgiref.sync import sync_to_async
import custom_settings
import discord
from discord.ext import commands
from bot.omni_bot import OmniBot
from pokemon.pokemond.main import PokemonObj, Pokedex, Player, Match
from pokemon.pokemond.names import *

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

    @commands.command(name="pokemon_info", help=PokemonDialog.GLOBALINFO)
    async def search_participant(self, ctx):
        message = PokemonDialog.CREATEMATCHMESSAGE
        channel = ctx.channel
        await channel.send(message)

    @commands.command(name='pokemon_whois', help=PokemonDialog.HELPPOKEMONINFO)
    async def pokemon_info(self, ctx, pokemon: str):

        try:
            pokedex = await sync_to_async(Pokedex)()
            pokemon = await sync_to_async(pokedex.get_pokemon)(pokemon)
            pokemonObj: PokemonObj = pokemon
            pokemon_type = get_pokemon_type(pokemonObj)
            pokemon_attacks = get_pokemon_attack(pokemonObj)
            message = discord.Embed(title=pokemonObj.name, type='rich')
            message.add_field(name="Type", inline=False, value=pokemon_type)
            message.add_field(name="Attaques", value=pokemon_attacks)
            message.add_field(name="Stats", value=get_pokemon_stats(pokemonObj))
            if pokemonObj.picture_url:
                message.set_thumbnail(url=pokemonObj.picture_url)
            await ctx.channel.send(embed=message)
        except KeyError:
            await ctx.channel.send("Ce pokemon n'existe pas !")

    @commands.command(name="pokemon_s", help=PokemonDialog.HELPGAMESUBSCRIPTION)
    async def game_subscription(self, ctx, pokemon: str):
        guild_id = ctx.guild.id
        guild = get_or_create(self.bot.storage['pokemon'], guild_id, {})
        participants: {} = get_or_create(guild, 'participants', {})
        get_or_create(guild, 'actions', {})
        pokemon_ids = pokemon.strip().split(',')
        if len(participants) < 2:
            pokedex = await sync_to_async(Pokedex)()
            player_pokemon = [
                await sync_to_async(pokedex.get_pokemon)(pokemon_id) for pokemon_id in pokemon_ids
            ]
            player = Player(ctx.message.author.id, ctx.message.author.name, player_pokemon)
            participants[ctx.message.author.id] = player
            await ctx.channel.send(PokemonDialog.SUBSCRIPTIONRECORDED)
        if len(participants) == 2:
            keys = list(participants.keys())
            await ctx.channel.send(PokemonDialog.ENOUGHPARTICIPANT.format(participants[keys[0]].name,
                                                                          participants[keys[0]].name))
            match = Match(player1=participants[keys[0]], player2=participants[keys[1]])
            match.start()
            guild['match'] = match
            await ctx.channel.send(PokemonDialog.STARTMATCH)

    @commands.command(name='pokemon_whoiam', help='Nope')
    async def get_user_info(self, ctx):
        try:
            player: Player = self.bot.storage['pokemon'][ctx.guild.id]['participants'][ctx.message.author.id]
        except KeyError:
            return
        embed = discord.Embed(title=player.name, type='rich', description="Liste des pokemon du joueur")
        for pokemon in player.pokemon:
            pokemon_attacks = get_pokemon_attack(pokemon)
            pokemon_type = get_pokemon_type(pokemon)
            pokemon_stats = get_pokemon_stats(pokemon, True)
            embed.add_field(name='Pokemon', value=pokemon.name + '\n' + pokemon_type, inline=True)
            embed.add_field(name='Attaques', value=pokemon_attacks, inline=True)
            embed.add_field(name='Stats', value=pokemon_stats, inline=True)
        await ctx.channel.send(embed=embed)

    @commands.command(name='pokemon_players', help='Nope')
    async def get_players_pokemon(self, ctx):
        players = self.bot.storage['pokemon'][ctx.guild.id]['participants']
        keys = list(players.keys())

        embed = discord.Embed(title="Joueurs", type='rich')

        player_1: Player = players[keys[0]]
        pokemon_1: PokemonObj = player_1.get_active_pokemon()

        player_2 = players[keys[1]] if len(keys) == 2 else None
        pokemon_2 = player_2.get_active_pokemon() if player_2 else None

        embed.add_field(name="Joueur", value=player_1.name, inline=player_2 is not None)
        if pokemon_2:
            embed.add_field(name="Joueur", value=player_2.name, inline=False)
        embed.add_field(name="Pokemon", value="{}\n{}".format(pokemon_1.name,
                                                              get_pokemon_type(pokemon_1)), inline=player_2 is not None)
        if pokemon_2:
            embed.add_field(name="Pokemon", value="{}\n{}".format(pokemon_2.name,
                                                                  get_pokemon_type(pokemon_2)),
                            inline=False)
        await ctx.channel.send(embed=embed)

    @commands.command(name="pokemon_f", help=PokemonDialog.HELPFIGHT)
    async def attack(self, ctx, action: str):
        guild_id = ctx.guild.id
        guild = self.bot.storage['pokemon'][guild_id]
        players = guild['participants']
        try:
            player = players[ctx.message.author.id]
            if action in [str(i) for i in range(1, 5)]:
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
        except KeyError:
            return
"""
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
"""


def get_or_create(base, key, init_data):
    try:
        return base[key]
    except KeyError:
        base[key] = init_data
        return base[key]


def get_player_by_id(players, user_id):
    for player in players:
        if player.user_id == user_id:
            return player
    return None


def get_pokemon_type(pokemon_obj: PokemonObj):
    pokemon_type = pokemon_obj.type1.name
    if pokemon_obj.type2:
        pokemon_type = pokemon_type + ' | ' + pokemon_obj.type2.name
    return pokemon_type


def get_pokemon_stats(pokemon_obj: PokemonObj, is_actual=False):
    if is_actual:
        stats = "\n".join(["* {}: {} -> {}".format(stat, pokemon_obj.initial_stats[stat], pokemon_obj.stats[stat])
                           for stat in
                           [PokemonStat.PV, PokemonStat.ATT,
                            PokemonStat.ATTSPE, PokemonStat.DEF,
                            PokemonStat.DEFSPE, PokemonStat.SPEED]])
    else:
        stats = "\n".join(["* {}: {}".format(stat, pokemon_obj.initial_stats[stat]) for stat in
                           [PokemonStat.PV, PokemonStat.ATT,
                            PokemonStat.ATTSPE, PokemonStat.DEF,
                            PokemonStat.DEFSPE, PokemonStat.SPEED]])
    return stats


def get_pokemon_attack(pokemon_obj: PokemonObj, is_actual=False):
    if is_actual:
        return
    else:
        attacks = "\n".join("* {}".format(pokemon_obj.capacities[capacity].name) for capacity in pokemon_obj.capacities)
    return attacks
