import os
try:
  import discord
except ImportError:
  print("Trying to Install required module: discord\n")
  os.system('python -m pip install discord')
  import discord
from discord.ext.commands import MissingPermissions
from discord.ext import commands, tasks
import random
import requests
from datetime import datetime
