import collections
import discord
from discord import Message
from discord.ext.commands import Bot


class OmniBot(Bot):
    storage = {'prefix': {},
               'forbid_channels': {},
               'deleted_messages': {},
               'deleted_messages_summary_channel': {},
               'pokemon': {}}

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

    async def on_message(self, message):
        ctx = await self.get_context(message)
        guild_id = ctx.guild.id
        if ctx.valid:
            if guild_id in self.storage['forbid_channels'] and ctx.channel.id in self.storage['forbid_channels'][guild_id]:
                return
            await self.process_commands(message)
            return
        if message.author == self.user and not message.content:
            return

    async def on_message_delete(self, message):
        ctx = await self.get_context(message)
        if ctx.valid:
            await self.process_commands(message)
            return

        if message.author == self.user and not message.content:
            return

        message_data = format_message(message)
        save_delete_message(message_data, guild_id=ctx.guild.id, storage=self.storage)

    async def on_reaction_add(self, reaction, user):
        """guild_id = reaction.message.guild.id

        # Pokemon
        if guild_id in self.storage['pokemon'] and "startMessage" in self.storage['pokemon'][guild_id]:
            if self.storage['pokemon'][guild_id]['startMessage'] == reaction.message.id:
                if 'participants' not in self.storage['pokemon'][guild_id]:
                    self.storage['pokemon'][guild_id]['participants'] = []
                self.storage['pokemon'][guild_id]['participants'].append(user.id)"""
        pass

    async def get_prefix(self, message):
        prefix = ret = self.command_prefix
        if message.guild.id in self.storage['prefix']:
            prefix = ret = self.storage['prefix'][message.guild.id]
        if callable(prefix):
            ret = await discord.utils.maybe_coroutine(prefix, self, message)

        if not isinstance(ret, str):
            try:
                ret = list(ret)
            except TypeError:
                # It's possible that a generator raised this exception.  Don't
                # replace it with our own error if that's the case.
                if isinstance(ret, collections.abc.Iterable):
                    raise

                raise TypeError("command_prefix must be plain string, iterable of strings, or callable "
                                "returning either of these, not {}".format(ret.__class__.__name__))

            if not ret:
                raise ValueError("Iterable command_prefix must contain at least one prefix")

        return ret


def format_message(message: Message):
    data = {"message": message.content,
            "id": message.id, "channel": message.channel.name, "channel_id": message.channel.id,
            'time': message.created_at.strftime("%b %d %Y %H:%M:%S"),
            "author_id": message.author.id, "author": message.author.name, 'attachment': len(message.attachments) != 0}
    return data


def save_delete_message(data, guild_id, storage):
    if guild_id not in storage["deleted_messages"]:
        storage["deleted_messages"][guild_id] = []
    storage["deleted_messages"][guild_id].append(data)
