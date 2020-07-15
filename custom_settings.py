from dotenv import load_dotenv
import pathlib
import django
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'omni_bot.settings'
django.setup()

INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.absolute(), "data")
load_dotenv()

TOKEN = os.environ.get('DISCORD_TOKEN')
