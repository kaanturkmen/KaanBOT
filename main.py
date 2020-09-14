# KaanBOT is a turkish discord bot. It is programmed to work in a single server.

# Importing packages.
import os
import requests

try:
  import requests
except ImportError:
  print("Trying to Install required module: requests\n")
  os.system('python -m pip install requests')

import requests
import shlex
import random
import discord
from discord.ext.commands import MissingPermissions
from discord.ext import commands, tasks
from datetime import datetime

# Control Panel for easy editing.
BOT_TOKEN = String
COMMAND_PREFIX = Character or String
SERVER_ID = Int
SERVER_LOG_CHANNEL_ID = Int
ADMINS_USER_ID = Int
CHANNEL_TO_UPDATE = Int
ADMIN_ROLE = 'Kaan'
MODERATOR_ROLE = 'Moderatör'


# Creating bot.
client = commands.Bot(command_prefix=COMMAND_PREFIX)

# Current time.
last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def bot_count():
    """
    A method which counts how many bots are in the server.
    :return: Integer value of bot count.
    """

    guild = client.get_guild(SERVER_ID)

    bot_counter = 0
    for member in guild.members:
        if member.bot:
            bot_counter += 1
    return bot_counter


# Displaying message, setting up status and starting update_user_count method when bot is ready.
@client.event
async def on_ready():

    # Setting bot status.
    activity = discord.Game(name=".y | github.com/katurkmen")
    await client.change_presence(status=discord.Status.online, activity=activity)

    # Starting user counting method.
    update_user_count.start()

    # Printing text when bot is ready.
    print('KaanBOT kullanıma hazır.')


# Sending user joined message to the server's log channel and direct messages to the newcomer.
@client.event
async def on_member_join(member):

    guild = client.get_guild(SERVER_ID)
    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    await channel.send(f'<@!{str(ADMINS_USER_ID)}> | {member.mention} sunucuya katıldı!')
    await member.send(
        f'Selam {member.mention}! Ben KaanBOT. CS Türkiye sunucusunun kodladığı bir botum ve bu sunucuda sana çeşitli'
        f' konularda yardım edeceğim. Öncelikle CS Türkiye discord sunucumuza hoş geldin! Seninle beraber'
        f' {guild.member_count - bot_count()} kişi olduk, katıldığın için çok mutluyuz. Bir sürü üniversite ve bölümden'
        f' insanların bulunduğu bu sunucuda umarım eğlenirsin. Bunlara ek olarak yazılımla ilgili her şey bu sunucuda'
        f' var,  dilediğinde insanlara yardım edip dilediğinde ise insanlardan yardım alabilirsin. İlk mesajını atmadan'
        f' önce kuralları okumayı unutma ve memnun kalmadığın bir şey olursa @Kaan ve @Moderatör taglarıyla mutlaka'
        f' bize ulaş. Kendine iyi bak, iyi eğlenceler! :computer:')


# Sending user joined message to the server's log channel.
@client.event
async def on_member_remove(member):

    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    await channel.send(f'<@!{str(ADMINS_USER_ID)}> | {member.mention} sunucudan çıktı!')


# Keeps track of user count in the server by renaming specified voice channel every 10 minutes.
@tasks.loop(minutes=10)
async def update_user_count():

    global last_update_time

    channel_to_change = client.get_channel(CHANNEL_TO_UPDATE)
    guild = client.get_guild(SERVER_ID)

    last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    await channel_to_change.edit(name=f'Üyeler: {guild.member_count - bot_count()}')


# Moderation commands which restricted by certain roles are given below this line. #

# Clears the current channel as specified amount of messages. If message count is not given, clears 5 messages.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def clear(ctx, amount=5):

    amount += 1
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'{amount} tane mesaj silindi.')


# Kicks user.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def kick(ctx, member: discord.Member, *, reason=None):

    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} isimli kullanıcı sunucudan atıldı.')


# Bans user.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def ban(ctx, member: discord.Member, *, reason=None):

    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} isimli kullanıcı banlandı.')


# Unbans user.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def unban(ctx, *, member):

    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} isimli kullanıcının banı kaldırıldı.')
            return


# Commands which give information about certain topics and usable by all member is given below this line.

# Custom command
@client.command()
async def ubuntu(ctx):

    await ctx.send('Ehmm... Sanırım kodu ubuntu code share\'dan paylaşman gerekiyordu. Kuralları okumuştun değil mi?'
                   ' :scream_cat:\nhttps://paste.ubuntu.com/')


# Custom command
@client.command()
async def ping(ctx):

    await ctx.send(f'Pingin şu anda {round(client.latency * 1000)}ms.')


# Custom command
@client.command()
async def senkimsin(ctx):

    await ctx.send('Merhaba! Ben KaanBOT, beni Kaan kodladı ve şu an Amerikada bir yerlerde kodum çalışıyor.'
                   ' Eğer ki çevirimdışı olursam fazla üzülmeyin, tahminen sunucum yeniden başlatılmıştır ve'
                   ' sunucunun açılması normalden daha uzun sürmüştür. Eğer bir hatam olursa, Kaan\'a bildirebilirsin.')


# Custom command
data = 'https://raw.githubusercontent.com/katurkmen/KaanBOT/master/main.py'
@client.command()
async def neyebenziyorsun(ctx):
    buffer = requests.get(data).text
    buffer = buffer.split('#')
    await ctx.send('Tahminen şöyle bir şeye: \n```python\n#' + buffer[random.randint(5, len(buffer) - 1)] + "\n```')


# Custom command
@client.command()
async def selam(ctx, member: discord.Member = None):

    if member is None:
        await ctx.send(f'Selaaam, {ctx.author.mention}!')
    else:
        await ctx.send(f'Selaaam, {member.mention}!')


# Custom command with aliases.
@client.command(aliases=['y', 'yardim', 'yardım'])
async def komutlar(ctx):

    await ctx.send('Sana nasıl yardımcı olabilirim? \n\n.ubuntu\n.ping\n.senkimsin\n.selam\n.acikkaynakkod'
                   '\n.neyebenziyorsun\n\nEğer ki sahip olmam gereken bir komut isterseniz, bunu Kaan\'a'
                   ' bildirebilirsiniz :)')


# Custom command
@client.command()
async def acikkaynakkod(ctx):

    await ctx.send('CS Türkiye <3 Açık Kaynak Kod!\nTakipte Kalın: https://github.com/katurkmen/')


# Custom command
@client.command()
async def projeler(ctx):

    await ctx.send('Şu an üstünde çalıştığım projeler:\n1) Selenium ile Web Scrapping Projesi (Java)\n'
                   '2) Oyun Projesi (Python)\n3) Discord Bot Projesi (Python)')


# Custom command
@client.command()
@commands.has_role(ADMIN_ROLE)
async def guncelleme(ctx):

    global last_update_time

    await ctx.send(f'Son kişi sayısı güncellemesi: {last_update_time}')


# If user tries to use some command which users does not have permission to use, replying it with error message.
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.send(":x: Bunu yapmaya yetkin yok!")
    else:
        print(error)


# Running the bot.
client.run(BOT_TOKEN)
