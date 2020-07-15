from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure
from bot.dialogs import *
from bot.omni_bot import OmniBot


class CommandOmni(commands.Cog, name='Omni'):

    def __init__(self, bot: OmniBot):
        self.bot = bot
        self.temp = {}

    @commands.command(name="pf", help='(ADMIN) Modifie la valeur à utiliser en prefix')
    @has_permissions(administrator=True)
    async def config(self, ctx, prefix: str = '?'):
        allowed_prefix = ['?', '!', '>', '<', '$']
        prefix = prefix.strip()
        channel = ctx.message.channel
        if prefix not in allowed_prefix:
            await channel.send("Oups ! Cette valeur n'est pas autorisée. "
                               "Essaie une de ces valeurs: {}".format(' '.join(allowed_prefix)))
            return

        guildId = ctx.guild.id
        self.bot.storage['prefix'][guildId] = prefix
        await channel.send("La valeur \"{}\" sera désormais utilisée comme préfix".format(prefix))

    @commands.command(name='fc', help=OMNIHELPFORBIDCHANNEL)
    @has_permissions(administrator=True)
    async def forbid_channel(self, ctx):
        guild_id = ctx.message.guild.id
        if guild_id not in self.bot.storage['forbid_channels']:
            self.bot.storage['forbid_channels'][guild_id] = []
        if ctx.message.channel.id not in self.bot.storage['forbid_channels'][guild_id]:
            self.bot.storage['forbid_channels'][guild_id].append(ctx.message.channel.id)
            await self.bot.get_channel(ctx.channel.id).send(OMNIFORBIDCHANNELSUCCESS.format(ctx.channel.name))
        else:
            self.bot.storage['forbid_channels'][guild_id].remove(ctx.message.channel.id)
            await self.bot.get_channel(ctx.channel.id).send(OMNIREMOVEFORBIDCHANNELSUCCESS.format(ctx.channel.name))

    @config.error
    @forbid_channel.error
    async def check_admin_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            pass


