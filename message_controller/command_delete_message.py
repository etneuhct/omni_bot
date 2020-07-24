from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure
from bot.omni_bot import OmniBot
from message_controller.dialogs import *


class CommandDeleteMessage(commands.Cog, name='Messages supprimés'):

    def __init__(self, bot: OmniBot):
        self.bot = bot
        self.temp = {}
        self.delete_save_message.start()

    @commands.command(name='dc', help=OMNIDELETESUMMARYCHAN)
    @has_permissions(administrator=True)
    async def set_delete_message_summary_channel(self, ctx):
        channel = ctx.message.channel
        self.bot.storage['deleted_messages_summary_channel'][ctx.message.guild.id] = channel.id
        await channel.send("Enregistré ! Le résumé sera désormais envoyé dans le channel {}".format(channel.name))

    @commands.command(name='dr', help='Affiche le résumé actuel des messages supprimé')
    async def show_delete_messages(self, ctx):
        guild_id = ctx.message.guild.id
        channel = ctx.message.channel
        if guild_id in self.bot.storage['deleted_messages']:
            message = get_deleted_messages_summary(self.bot.storage['deleted_messages'][ctx.message.guild.id])
        else:
            message = "Oups ! On dirait qu'aucun message n'a été supprimé"
        await channel.send(message)

    @tasks.loop(hours=24)
    async def delete_save_message(self):
        if len(self.bot.storage['deleted_messages']) == 0:
            return
        for guild_id in self.bot.storage['deleted_messages']:
            if len(self.bot.storage['deleted_messages'][guild_id]) > 0 \
                    and guild_id in self.bot.storage['deleted_messages_summary_channel']:
                channel_id = self.bot.storage['deleted_messages_summary_channel'][guild_id]
                message = get_deleted_messages_summary(self.bot.storage['deleted_messages'][guild_id])
                await self.bot.get_channel(channel_id).send(message)
        self.bot.storage['deleted_messages'] = {}

    @delete_save_message.before_loop
    async def before_delete(self):
        await self.bot.wait_until_ready()

    @set_delete_message_summary_channel.error
    async def check_admin_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            pass


def get_deleted_messages_summary(messages_data):
    message = "Au cours du dernier enregistrement, les messages suivants ont été supprimés:\n*********\n{}\n*********" \
        .format("\n\n".join(
        [
            "Par {author} le {time} dans le channel {channel}"
            "\n-----"
            "\n\"{message}\""
            "\n-----".format(**data) for data in messages_data
        ]))
    return message
