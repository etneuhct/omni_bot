import custom_settings
from bot.command_omni import CommandOmni
from bot.omni_bot import OmniBot
from message_controller.command_delete_message import CommandDeleteMessage
from pendu.command_pendu import CommandPendu
from pokemon.command_pokemon import CommandPokemon
from pokemon.models import Pokemon

allowed_cmd = [CommandPendu, CommandOmni, CommandDeleteMessage, CommandPokemon]

omni_bot = OmniBot(command_prefix="?")
for cmd in allowed_cmd:
    omni_bot.add_cog(cmd(omni_bot))
omni_bot.run(custom_settings.TOKEN)


