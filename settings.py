import os

from dotenv import load_dotenv
import pathlib

INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.absolute(), "data")
load_dotenv()

TOKEN = os.environ.get('DISCORD_TOKEN') #os.getenv('DISCORD_TOKEN')
