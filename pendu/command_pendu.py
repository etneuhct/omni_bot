from discord.ext import commands
from pendu.pendu import Pendu
from utils import help, dialogs


class CommandPendu(commands.Cog, name='Le pendu'):

    def __init__(self, bot):
        self.bot = bot
        self.temp = {}

    @commands.command(name="ps", help=help.pendu)
    async def pendu(self, ctx, move_number: int = 5, minimum_letter_number: int = 6,
                    maximum_letter_number: int = 8, language: str = 'fr'):

        guildId = ctx.guild.id
        if guildId not in self.bot.storage:
            self.bot.storage[guildId] = {}
        try:
            pendu = Pendu(nombre_coup=move_number,
                          minimum_letter=minimum_letter_number,
                          maximum_letter=maximum_letter_number,
                          language=language)
        except IndexError:
            await ctx.message.channel.send(dialogs.PENDUNOWORDMATCHING)
            return
        self.bot.storage[guildId]["pendu"] = pendu
        message = dialogs.PENDUCOUPRESTANT.format(pendu.getCoupRestant()) + '\n' + pendu.getMot()
        sent_message = await ctx.message.channel.send(message)
        self.temp = {guildId: sent_message}

    @commands.command(name="pc", help=help.pendu_check)
    async def pendu_check(self, ctx, letter: str = ' '):
        guildId = ctx.guild.id
        channel = ctx.message.channel

        if guildId not in self.bot.storage or "pendu" not in self.bot.storage[guildId]:
            await channel.send(dialogs.PENDUNOPARTY)
            return
        letter = letter[0]
        pendu = self.bot.storage[guildId]['pendu']
        if pendu.getCoupRestant() < 1:
            await channel.send(dialogs.PENDULOOSE)
            return
        found_letter = pendu.checkLettre(letter)
        if found_letter == -1:
            await channel.send(dialogs.PENDUALREADYUSED.format(letter))
            return

        message_mot = pendu.getMot()
        message_use = dialogs.PENDUUSEDLETTER.format(", ".join(pendu.lettreDejaUse))
        first_step = message_mot + '\n' + message_use

        if not found_letter:
            error_message = dialogs.PENDUCOUPRESTANT.format(pendu.getCoupRestant())
            bonhomme_message = pendu.getBonhomme()
            error = first_step + '\n' + error_message + '\n' + bonhomme_message

            await channel.send(error)
        else:
            await channel.send(first_step)

        if pendu.getCoupRestant() < 1:
            end_message = dialogs.PENDUENDGAME.format(pendu.mot)
            await channel.send(end_message)
