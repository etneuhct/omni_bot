from games.pendu.command_pendu import CommandPendu
import settings
from games.pokemon.command_pokemon import CommandPokemon
from omni_bot.command_omni import CommandOmni
from omni_bot.omni_bot import OmniBot
from tools.delete_message.command_delete_message import CommandDeleteMessage

allowed_cmd = [CommandPendu, CommandOmni, CommandDeleteMessage, CommandPokemon]

omni_bot = OmniBot(command_prefix="?")
for cmd in allowed_cmd:
    omni_bot.add_cog(cmd(omni_bot))
omni_bot.run(settings.TOKEN)
