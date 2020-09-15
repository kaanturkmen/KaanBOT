# KaanBOT is a turkish discord bot. It is programmed to work in a single server.

# Importing packages.
from Imports import *

# Getting bot settings in.
from Settings import *

# Creating bot.
client = commands.Bot(command_prefix=COMMAND_PREFIX)

# Current time.
last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Running the bot.
def main():
    client.run(BOT_TOKEN)


# <- Intentionally
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

    # Setting up bot status.
    activity = discord.Activity(type=discord.ActivityType.watching,
                                name="Komutlar için " + COMMAND_PREFIX + "y" + "  yazınız.")

    await client.change_presence(status=discord.Status.online, activity=activity)

    # Starting user count method.
    update_user_count.start()

    # Printing information of bot on the console.
    print(
        """

Powered by KaanBot Base
-------------------------------------
%s hazır!
discord.py Versiyonu: %s
Komut İmleci: '%s'

Tüm sorularınız için: https://discord.gg/CRy8eER
-------------------------------------

        """ % (client.user.name, discord.__version__, COMMAND_PREFIX)
    )


# Sending user joined message to the server's log channel and direct messages to the newcomer.
@client.event
async def on_member_join(member):

    guild = client.get_guild(SERVER_ID)
    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    await channel.send(f'<@!{str(ADMINS_USER_ID)}> | {member.mention} sunucuya katıldı!')
    await member.send(
        f"Selam {member.mention}! Ben KaanBOT. CS Türkiye sunucusunun kodladığı bir botum ve bu sunucuda sana çeşitli"
        f" konularda yardım edeceğim. Öncelikle CS Türkiye discord sunucumuza hoş geldin! Seninle beraber"
        f" {guild.member_count - bot_count()} kişi olduk, katıldığın için çok mutluyuz. Bir sürü üniversite ve bölümden"
        f" insanların bulunduğu bu sunucuda umarım eğlenirsin. Bunlara ek olarak yazılımla ilgili her şey bu sunucuda"
        f" var,  dilediğinde insanlara yardım edip dilediğinde ise insanlardan yardım alabilirsin. İlk mesajını atmadan"
        f" önce kuralları okumayı unutma ve memnun kalmadığın bir şey olursa @Kaan ve @Moderatör taglarıyla mutlaka"
        f" bize ulaş. Kendine iyi bak, iyi eğlenceler! :computer:")


# Sending user joined message to the server's log channel.
@client.event
async def on_member_remove(member):

    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)
    await channel.send(f"<@!{str(ADMINS_USER_ID)}> | {member.mention} sunucudan çıktı!")


# Keeps track of user count in the server by renaming specified voice channel every 10 minutes.
@tasks.loop(minutes=10)
async def update_user_count():

    global last_update_time
    channel_to_change = client.get_channel(CHANNEL_TO_UPDATE_ID)
    guild = client.get_guild(SERVER_ID)
    last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await channel_to_change.edit(name=f"Üyeler: {guild.member_count - bot_count()}")


# Clears the current channel as specified amount of messages. If message count is not given, clears 5 messages.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def clear(ctx, amount=5):

    amount += 1
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"{amount} tane mesaj silindi.")


# Kicks user.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def kick(ctx, member: discord.Member, *, reason=None):

    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} isimli kullanıcı sunucudan atıldı.")


# Bans user.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def ban(ctx, member: discord.Member, *, reason=None):

    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} isimli kullanıcı banlandı.")


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
            await ctx.send(f"{user.mention} isimli kullanıcının banı kaldırıldı.")
            return


# updates user count on server.
@client.command()
@commands.has_role(ADMIN_ROLE)
async def guncelleme(ctx):

    global last_update_time
    await ctx.send(f"Son kişi sayısı güncellemesi: {last_update_time}")


# Custom command
@client.command()
async def pastebin(ctx):

    await ctx.send("Ehmm... Sanırım kodu ubuntu pastebin\'den paylaşman gerekiyordu. Kuralları okumuştun değil mi?"
                   " :scream_cat:\nhttps://paste.ubuntu.com/")


# Custom command
@client.command()
async def ping(ctx):

    await ctx.send(f"Pingin şu anda {round(client.latency * 1000)}ms.")


# Custom command
@client.command()
async def senkimsin(ctx):

    await ctx.send("Merhaba! Ben KaanBOT, Kaan\'ın kodladığı açık kaynak kodlu bir botum ve şu an"
                   " Amerikada bir yerlerde kodum çalışıyor. Kodlarıma <https://github.com/katurkmen/KaanBOT>"
                   " adresiden ulaşabilirsiniz. Eğer ki çevirimdışı olursam fazla üzülmeyin, tahminen sunucum yeniden"
                   " başlatılmıştır veya kodum güncelleniyordur. Eğer bir hatam olursa, Kaan\'a bildirebilirsin."
                   " İyi eğlenceler!")


# Custom command
@client.command()
async def neyebenziyorsun(ctx):

    buffer = requests.get('https://raw.githubusercontent.com/katurkmen/KaanBOT/master/main.py').text.split('#')
    await ctx.send('Tahminen şöyle bir şeye: \n```python\n#' + buffer[random.randint(5, len(buffer) - 1)] + "\n```")


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

    await ctx.send("""
Sana nasıl yardımcı olabilirim? 

""" + COMMAND_PREFIX + """pastebin
""" + COMMAND_PREFIX + """ping
""" + COMMAND_PREFIX + """senkimsin
""" + COMMAND_PREFIX + """selam
""" + COMMAND_PREFIX + """sosyal
""" + COMMAND_PREFIX + """acikkaynakkod
""" + COMMAND_PREFIX + """neyebenziyorsun
""" + COMMAND_PREFIX + """istek

Eğer ki sahip olmam gereken bir komut isterseniz, bunu Kaan\'a bildirebilirsiniz :)
""")


# Custom command
@client.command()
async def acikkaynakkod(ctx):

    await ctx.send('CS Türkiye <3 Açık Kaynak Kod!\nTakipte Kalın: <https://github.com/katurkmen/>')


# Custom command
@client.command()
async def projeler(ctx):

    await ctx.send("""
Şu an üstünde çalıştığım projeler:
1) Selenium ile Web Scrapping Projesi (Java)
2) Oyun Projesi (Python)
3) Discord Bot Projesi (Python)
""")


# If user tries to use some command which users does not have permission to use, replying it with error message.
@client.event
async def on_command_error(ctx, error):

    if isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.send(":x: Bunu yapmaya yetkin yok!")
    else:
        print(error)


@client.command()
async def sosyal(ctx):

    await ctx.send("""
    
● Youtube: <https://www.youtube.com/channel/UCyd_GxfGPpWtx9upRc7arhg>

● Github: <https://github.com/katurkmen/>

● Twitter: <https://twitter.com/katurkmenn/>

● Instagram: <https://instagram.com/katurkmenn/>

""")


# Custom Command
@client.command()
async def istek(ctx, *, request=None):
    if request is not None:

        await ctx.send(f"İsteğin kaydedildi. Teşekkür ederiz!")

        channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

        await channel.send(f"<@!{str(ADMINS_USER_ID)}> | {ctx.author.mention}\'dan gelen"
                           f" komut isteği: {request}")
    else:

        await ctx.send(f"Lütfen geçerli bir istek giriniz. Örneğin,\n\n{COMMAND_PREFIX}istek Müzik özelliği eklenmeli!")


# Shutdown Catcher & Ignition
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Goodbye!')
        try:
            os._exit(0)
        except SystemExit:
            os._exit(0)
