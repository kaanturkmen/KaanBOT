# Importing packages.
import discord
from discord.ext.commands import MissingPermissions
from discord.ext import commands, tasks

from Email import send_email

import random
import requests
from datetime import datetime

from Settings import *

# Creating intents for bot privilidges.
intents = discord.Intents()
intents = intents.all()

# Creating the bot.
client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Removing help command.
client.remove_command('help')

# Current time.
last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

date = datetime.today().strftime('%Y-%m-%d')

# Email Dictionary
email_dict = {}


# Running the bot.
def main():
    client.run(BOT_TOKEN)


# Creates a simple format of embeddings.
def create_embed():
    embed = discord.Embed(title="", color=EMBED_COLOR)
    embed.set_author(name=EMBED_NAME, url=EMBED_URL,
                     icon_url=EMBED_ICON_URL)

    return embed


def check_if_university(user_email: str):
    try:
        pure_email = user_email.strip().split('@')
        after_at = pure_email[1]
        split_from_dots = after_at.split('.')
        last_two_parts = split_from_dots[len(split_from_dots) - 2], split_from_dots[len(split_from_dots) - 1]

        for element in last_two_parts:
            if element == 'edu':
                return True

        return False
    except Exception as e:
        print(e)
        return None


# Returns bot count.
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

    print("Bot is running.")


# Sending user joined message to the server's log channel and direct messages to the newcomer.
@client.event
async def on_member_join(member):
    guild = client.get_guild(SERVER_ID)
    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    embed = create_embed()
    embed.add_field(name=":warning: Bilgilendirme",
                    value=f"{member.mention} sunucuya katıldı!", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await channel.send(embed=embed)

    try:
        await member.send(
            f"Selam {member.mention}! Ben KaanBOT. CS Türkiye sunucusunun moderasyonunu sağlamakla görevliyim ve"
            f" bu sunucuda sana çeşitli"
            f" konularda yardım edeceğim. Öncelikle CS Türkiye discord sunucumuza hoş geldin! Seninle beraber"
            f" {guild.member_count - bot_count()} kişi olduk, katıldığın için çok mutluyuz. Birçok üniversite ve bölümden"
            f" insanların bulunduğu bu sunucuda umarım eğlenirsin. Bunlara ek olarak yazılımla ilgili her şey bu sunucuda"
            f" var,  dilediğinde insanlara yardım edip dilediğinde ise insanlardan yardım alabilirsin. İlk mesajını atmadan"
            f" önce kuralları okumayı unutma ve memnun kalmadığın bir şey olursa @Kaan veya @Moderatör taglarıyla mutlaka"
            f" bize ulaş. Kendine iyi bak, iyi eğlenceler! :computer:")
    except discord.errors.Forbidden:
        print("Cannot send a message to the user.")


# Sending user joined message to the server's log channel.
@client.event
async def on_member_remove(member):
    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)
    embed = create_embed()

    embed.add_field(name=":warning: Bilgilendirme",
                    value=f"{member.mention} sunucudan çıktı!", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await channel.send(embed=embed)


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

    embed = create_embed()
    embed.add_field(name=":warning: Bilgilendirme",
                    value=f"{amount} tane mesaj silindi.", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await ctx.send(embed=embed)


# Kicks user.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)

    embed = create_embed()
    embed.add_field(name=":warning: Bilgilendirme",
                    value=f"{member.mention} isimli kullanıcı sunucudan atıldı.", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await ctx.send(embed=embed)


# Bans user.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)

    embed = create_embed()
    embed.add_field(name=":warning: Bilgilendirme",
                    value=f"{member.mention} isimli kullanıcı sunucudan yasaklandı.", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await ctx.send(embed=embed)


# Unbans user.
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split(MEMBER_DISCRIMINATOR_SIGN)

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)

            embed = create_embed()
            embed.add_field(name=":warning: Bilgilendirme",
                            value=f"{user.mention} isimli kullanıcının banı kaldırıldı.", inline=False)
            embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

            await ctx.send(embed=embed)
            return


# Custom command
@client.command()
async def ping(ctx):
    embed = create_embed()
    embed.add_field(name=":warning: Bilgilendirme",
                    value=f"Pingim şu anda {round(client.latency * 1000)}ms.", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await ctx.send(embed=embed)


# Custom command
@client.command()
async def neyebenziyorsun(ctx):
    buffer = requests.get('https://raw.githubusercontent.com/katurkmen/KaanBOT/master/main.py').text.split('#')

    embed = create_embed()
    embed.add_field(name=":warning: Bilgilendirme",
                    value="Tahminen şöyle bir şeye:\n```python\n" + buffer[
                        random.randint(5, len(buffer) - 1)] + "\n```", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await ctx.send(embed=embed)


# Custom command
@client.command()
async def selam(ctx, member: discord.Member = None):
    buffer = requests.get('https://raw.githubusercontent.com/katurkmen/KaanBOT/master/main.py').text.split('#')

    embed = create_embed()

    if member is None:
        embed.add_field(name=':heart_eyes: :heart_eyes: :heart_eyes:', value=f'Selaaam, {ctx.author.mention}!',
                        inline=False)
    else:
        embed.add_field(name=':heart_eyes: :heart_eyes: :heart_eyes:', value=f'Selaaam, {member.mention}!',
                        inline=False)

    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await ctx.send(embed=embed)


# Custom command with aliases.
@client.command(aliases=['y', 'yardim', 'yardım'])
async def komutlar(ctx):
    embed = create_embed()
    embed.add_field(name=":warning: Bilgilendirme",
                    value="\nSana nasıl yardımcı olabilirim?\n\n" + COMMAND_PREFIX + "ping\n" + COMMAND_PREFIX + "selam\n"
                          + COMMAND_PREFIX + "sosyal\n" + COMMAND_PREFIX + "neyebenziyorsun\n" + COMMAND_PREFIX +
                          "istek\n\nEğer ki sahip olmam gereken bir komut isterseniz, bunu Kaan\'a bildirebilirsiniz"
                          " :)\n", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await ctx.send(embed=embed)


# If user tries to use some command which users does not have permission to use, replying it with error message.
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CheckFailure):
        embed = create_embed()
        embed.add_field(name=":x: İşlem Başarısız.",
                        value="Bunu yapmaya yetkin yok.", inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

        await ctx.send(embed=embed)
    else:
        print(error)


# Custom Command
@client.command()
async def sosyal(ctx):
    embed = create_embed()
    embed.add_field(name=":warning: Bilgilendirme",
                    value="● Youtube: <https://www.youtube.com/channel/UCyd_GxfGPpWtx9upRc7arhg>\n\n"
                          "● Github: <https://github.com/katurkmen/>\n\n● Twitter: <https://twitter.com/katurkmenn/>\n\n"
                          "● Instagram: <https://instagram.com/katurkmenn/>\n\n", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

    await ctx.send(embed=embed)


# Custom Command
@client.command()
async def istek(ctx, *, request=None):
    if request is not None:

        embed = create_embed()
        embed.add_field(name=":warning: Bilgilendirme",
                        value="İsteğin kaydedildi. Teşekkür ederiz!", inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

        await ctx.send(embed=embed)

        channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

        embed = create_embed()
        embed.add_field(name=":warning: Bilgilendirme",
                        value=f"{ctx.author.mention}\'dan gelen"
                              f" komut isteği: {request}", inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

        await channel.send(embed=embed)

    else:

        embed = create_embed()
        embed.add_field(name=":warning: Bilgilendirme",
                        value=f"Lütfen geçerli bir istek girin. Örneğin,\n\n{COMMAND_PREFIX}istek Müzik özelliği eklenmeli!",
                        inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

        await ctx.send(embed=embed)


# Custom Command
@client.command()
async def basvuru(ctx, email=None, *, major=None):
    await ctx.channel.purge(limit=1)

    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    user_id = ctx.message.author.id
    user_email = email
    is_university_email = check_if_university(user_email)
    user_major = major

    if user_email is None:
        embed = create_embed()
        embed.add_field(name=":x: İşlem başarısız.",
                        value=f"{ctx.author.mention} | Lütfen bir mail adresi girin.",
                        inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
        await ctx.send(embed=embed)
        return

    if user_major is None:
        embed = create_embed()
        embed.add_field(name=":x: İşlem başarısız.",
                        value=f"{ctx.author.mention} | Lütfen başvuru yaparken bölümünüzü belirtin.",
                        inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
        await ctx.send(embed=embed)
        return

    if not is_university_email:
        embed = create_embed()
        embed.add_field(name=":x: İşlem başarısız.",
                        value=f"{ctx.author.mention} | Girdiğiniz mail adresi bir üniversiteye ait değildir, lütfen"
                              f" bir üniversite mail adresi giriniz.",
                        inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
        await ctx.send(embed=embed)
        return

    if user_id in email_dict:
        embed = create_embed()
        embed.add_field(name=":warning: İşlem başarısız.",
                        value=f"{ctx.author.mention} | Başvurunuz mevcut, lütfen .onayla komutu ile kendinizi"
                              f" onaylayınız.",
                        inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
        await ctx.send(embed=embed)
        return

    user_n = ctx.message.author.name
    user_key = send_email(user_n, email)

    if user_key is None:
        embed = create_embed()
        embed.add_field(name=":warning: Hata",
                        value=f"{ctx.author.mention} | Bir şeyler yanlış gitti, lütfen bir yetkiliye bu durumu bildiriniz.",
                        inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
        await ctx.send(embed=embed)
        return

    email_dict[user_id] = (user_n, int(user_key), user_email, user_major)

    embed = create_embed()
    embed.add_field(name=":white_check_mark: İşlem Başarılı.",
                    value=f"{ctx.author.mention} | Üniversite başvurunuz alınmıştır, lütfen mailinizi kontrol ediniz.",
                    inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
    await ctx.send(embed=embed)

    embed = create_embed()
    embed.add_field(name="Üniversite Rolü Başvurusu Alındı.",
                    value=f"{ctx.author.mention} isimli üyenin bölümü {user_major} olup üniversite rolü başvurusu alınmıştır."
                          f" Lütfen onaylanma mesajını bekleyiniz.",
                    inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
    await channel.send(embed=embed)


# Custom Command
@client.command()
async def onayla(ctx, code=None):
    await ctx.channel.purge(limit=1)
    user_id = ctx.message.author.id
    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    if user_id not in email_dict.keys():
        embed = create_embed()
        embed.add_field(name=":x: İşlem Başarısız.",
                        value=f"{ctx.author.mention} | Başvurunuz bulunamadı, lütfen .basvuru yazıp bir başvuru yapınız.",
                        inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
        await ctx.send(embed=embed)
        return

    if code is None:
        embed = create_embed()
        embed.add_field(name=":x: İşlem Başarısız.",
                        value=f"{ctx.author.mention} | Lütfen kod giriniz.",
                        inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
        await ctx.send(embed=embed)
        return

    if not email_dict[user_id][1] == int(code):
        embed = create_embed()
        embed.add_field(name=":x: İşlem Başarısız.",
                        value=f"{ctx.author.mention} | Girdiğiniz kod hatalı, lütfen tekrar deneyiniz.",
                        inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
        await ctx.send(embed=embed)
        return

    embed = create_embed()
    embed.add_field(name=":white_check_mark: İşlem Başarılı.",
                    value=f"{ctx.author.mention} | Başvurunuz onaylanmıştır. Lütfen bir yetkilinin size rol vermesini bekleyin.",
                    inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
    await ctx.send(embed=embed)

    embed = create_embed()
    embed.add_field(name=":white_check_mark: Kullanıcının Üniversite başvurusu onaylandı.",
                    value=f"{ctx.author.mention}'nın üniversite başvurusu onaylanmıştır. Kullanıcıya rol verebilirsiniz.",
                    inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
    await channel.send(embed=embed)


# Custom Command
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def botbildir(ctx, channel: discord.TextChannel, *, msg: str):
    channel = client.get_channel(channel.id)
    await channel.send(msg)


# Custom Command
@client.command()
@commands.has_role(ADMIN_ROLE)
async def botdm(ctx, member: discord.Member, *, msg: str):
    channel = await member.create_dm()
    msg += "\n\n```NOT: KaanBOT'a Atılan Mesajlar Bize Ulaşmamaktadır.```"
    await channel.send(msg)


# Custom Command
@client.command()
@commands.has_role(ADMIN_ROLE)
async def kayitlog(ctx):
    channel = await ctx.author.create_dm()
    await channel.send(email_dict)


# Custom Command
@client.command()
@commands.is_owner()
async def offlineol(ctx, channel: discord.TextChannel):
    channel = client.get_channel(channel.id)

    msg = """

KaanBOT kapatılıyor, ikinci bir duyuruya kadar lütfen komutlarımı kullanmaya çalışmayınız!

Kapatılma nedenim şunlardan biri olabilir:
\t ● Sunucuma güncelleme geldi ve yeniden başlatılıyorum.
\t ● Bana yeni komutlar ekleniyor ve artık daha fazla komut destekleyeceğim.
\t ● Kodumda olmaması gereken bir hata farkedildi ve bunu düzeltmek istiyorlar.

En azından bana söylenen bu şekilde, beni geliştirenler her bilgiyi benimle paylaşmıyorlar :(

Görüşmek üzere! ^-^

Computer Science Türkiye

"""

    embed = create_embed()
    embed.add_field(name="KaanBOT aktif.",
                    value=msg + "||@everyone||", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
    await channel.send(embed=embed)
    print("Bot is being shut down.")
    await ctx.bot.logout()


# Custom Command
@client.command()
@commands.is_owner()
async def onlineol(ctx, channel: discord.TextChannel):
    channel = client.get_channel(channel.id)

    msg = """

Sizi yeniden gördüğüme sevindim!

Kodumda nelerin değiştiğini öğrenmek isterseniz githubdaki commitlerime bakabilirsiniz.

Buralarda olacağım, hepinize iyi eğlenceler. ^-^

Computer Science Türkiye

Değişen kodları görmek için:
<https://github.com/katurkmen/KaanBOT/commits/master>

"""

    embed = create_embed()
    embed.add_field(name="KaanBOT aktif.",
                    value=msg + "||@everyone||", inline=False)
    embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)
    await channel.send(embed=embed)


# Custom Command
@client.command()
@commands.has_any_role(ADMIN_ROLE, MODERATOR_ROLE)
async def kayitsil(ctx, member: discord.Member):
    key = member.id
    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    if ctx.author.id != ADMINS_USER_ID:
        embed = create_embed()
        embed.add_field(name=":warning: Bilgilendirme",
                        value=f"{ctx.author.mention} isimli yetkili kayıtsil methodunu çalıştırdı.", inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

        await channel.send(embed=embed)

    if key in email_dict.keys():

        embed = create_embed()
        embed.add_field(name=":warning: Bilgilendirme",
                        value=f'``` {key, email_dict.get(key)} isimli girdi silindi.```', inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

        await channel.send(embed=embed)

        email_dict.pop(key, None)

        embed = create_embed()
        embed.add_field(name=":white_check_mark: İşlem Başarılı",
                        value=f'{member.mention}\'ın kaydı silindi.', inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

        await channel.send(embed=embed)
    else:
        embed = create_embed()
        embed.add_field(name=":white_check_mark: İşlem Başarılı",
                        value=f'{member.mention} ile ilgili kayıt bulunamadı.', inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

        await ctx.send(embed=embed)

        embed = create_embed()
        embed.add_field(name=":x: İşlem Başarısız",
                        value="Bir girdi silinemedi.", inline=False)
        embed.add_field(name="İyi eğlenceler dileriz.", value="CS Türkiye Yönetimi", inline=True)

        await channel.send(embed=embed)


if __name__ == '__main__':
    main()
