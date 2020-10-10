# Importing packages.
import discord
from discord.ext.commands import MissingPermissions
from discord.ext import commands, tasks

from Email import send_email

import random
import requests
from datetime import datetime
import json

from Settings import *

# Creating the bot.
client = commands.Bot(command_prefix=COMMAND_PREFIX)

# Current time.
last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

date = datetime.today().strftime('%Y-%m-%d')

# Email Dictionary
email_dict = {}


# Running the bot.
def main():
    client.run(BOT_TOKEN)


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
    except:
        return None


# <- It is put intentionally for parsing.
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
    save_and_delete_emails.start()

    # Printing information of bot on the console.
    print("\nPowered by KaanBot Base\n-------------------------------------\n%s hazır!\ndiscord.py Versiyonu:"
          " %s\nKomut İmleci: '%s'\n\nTüm sorularınız için: https://discord.gg/CRy8eER"
          "\n-------------------------------------\n" % (client.user.name, discord.__version__, COMMAND_PREFIX))


# Sending user joined message to the server's log channel and direct messages to the newcomer.
@client.event
async def on_member_join(member):
    guild = client.get_guild(SERVER_ID)
    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    await channel.send(f'<@!{str(ADMINS_USER_ID)}> | {member.mention} sunucuya katıldı!')
    await member.send(
        f"Selam {member.mention}! Ben KaanBOT. CS Türkiye sunucusunun moderasyonunu sağlamakla görevliyim ve"
        f" bu sunucuda sana çeşitli"
        f" konularda yardım edeceğim. Öncelikle CS Türkiye discord sunucumuza hoş geldin! Seninle beraber"
        f" {guild.member_count - bot_count()} kişi olduk, katıldığın için çok mutluyuz. Birçok üniversite ve bölümden"
        f" insanların bulunduğu bu sunucuda umarım eğlenirsin. Bunlara ek olarak yazılımla ilgili her şey bu sunucuda"
        f" var,  dilediğinde insanlara yardım edip dilediğinde ise insanlardan yardım alabilirsin. İlk mesajını atmadan"
        f" önce kuralları okumayı unutma ve memnun kalmadığın bir şey olursa @Kaan veya @Moderatör taglarıyla mutlaka"
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
                   " Amerika'da bir yerlerde kodum çalışıyor. Kodlarıma <https://github.com/katurkmen/KaanBOT>"
                   " adresiden ulaşabilirsiniz. Eğer ki çevrim dışı olursam fazla üzülmeyin, tahminen sunucum yeniden"
                   " başlatılmıştır veya kodum güncelleniyordur. Eğer bir hatam olursa, Kaan\'a bildirebilirsin."
                   " İyi eğlenceler!")


# Custom command
@client.command()
async def neyebenziyorsun(ctx):
    buffer = requests.get('https://raw.githubusercontent.com/katurkmen/KaanBOT/master/main.py').text.split('#')
    await ctx.send("Tahminen şöyle bir şeye:\n```python\n" + buffer[random.randint(5, len(buffer) - 1)] + "\n```")


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
    await ctx.send("\nSana nasıl yardımcı olabilirim?\n\n" + COMMAND_PREFIX + "pastebin\n" + COMMAND_PREFIX +
                   "ping\n" + COMMAND_PREFIX + "senkimsin\n" + COMMAND_PREFIX + "selam\n" + COMMAND_PREFIX +
                   "sosyal\n" + COMMAND_PREFIX + "acikkaynakkod\n" + COMMAND_PREFIX + "neyebenziyorsun\n" +
                   COMMAND_PREFIX + "istek\n\nEğer ki sahip olmam gereken bir komut isterseniz,"
                                    " bunu Kaan\'a bildirebilirsiniz :)\n")


# Custom command
@client.command()
async def acikkaynakkod(ctx):
    await ctx.send('CS Türkiye <3 Açık Kaynak Kod!\nTakipte Kalın: <https://github.com/katurkmen/>')


# Custom command
@client.command()
async def projeler(ctx):
    await ctx.send("Şu an üstünde çalıştığım projeler:\n1) Selenium ile Web Scrapping Projesi (Java)\n2) Oyun Projesi"
                   " (Python)\n3) Discord Bot Projesi (Python)")


# If user tries to use some command which users does not have permission to use, replying it with error message.
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.send(":x: Bunu yapmaya yetkin yok!")
    else:
        print(error)


# Custom Command
@client.command()
async def sosyal(ctx):
    await ctx.send("● Youtube: <https://www.youtube.com/channel/UCyd_GxfGPpWtx9upRc7arhg>\n\n"
                   "● Github: <https://github.com/katurkmen/>\n\n● Twitter: <https://twitter.com/katurkmenn/>\n\n"
                   "● Instagram: <https://instagram.com/katurkmenn/>\n\n")


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


@client.command()
async def basvuru(ctx, email=None, *, major=None):
    await ctx.channel.purge(limit=1)

    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    if email is not None:
        user_id = ctx.message.author.id
        user_email = email
        is_university_email = check_if_university(user_email)
        user_major = major

        if MODERATOR_ROLE.lower() in [x.name.lower() for x in ctx.message.author.roles] or ADMIN_ROLE.lower() in [
            y.name.lower() for y in ctx.message.author.roles]:
            if is_university_email:
                user_n = ctx.message.author.name
                user_key = send_email(user_n, email)
                if user_key is None:
                    await ctx.send(f':warning: {ctx.author.mention}, bir şeyler yanlış gitti.'
                                   f' <@!{str(ADMINS_USER_ID)}>')
                else:
                    if email_dict[user_id] is None:
                        email_dict[user_id] = []
                        email_dict[user_id].append((user_n, int(user_key), user_email, user_major))
                    else:
                        email_dict[user_id].append([])
                    await ctx.send(f':white_check_mark: {ctx.author.mention}, üniversite rolü başvurunuz alınmıştır.'
                                   f' Mailinizi kontrol ediniz!')
            else:
                await ctx.send(f':x: {ctx.author.mention}, girdiğiniz mail adresi bir üniversiteye ait değildir,'
                               f' lütfen tekrar deneyiniz.')
        else:
            if user_id not in email_dict:
                if is_university_email:
                    user_n = ctx.message.author.name
                    user_key = send_email(user_n, email)
                    if user_major is not None:
                        if user_key is None:
                            await ctx.send(f':warning: {ctx.author.mention}, bir şeyler yanlış gitti.'
                                           f' <@!{str(ADMINS_USER_ID)}>')
                        else:
                            email_dict[user_id] = (user_n, int(user_key), user_email, user_major)
                            await ctx.send(
                                f':white_check_mark: {ctx.author.mention}, üniversite rolü başvurunuz alınmıştır.'
                                f' Mailinizi kontrol ediniz!')
                            await channel.send(
                                f'<@!{str(ADMINS_USER_ID)}> | {ctx.author.mention}\'nin üniversite başvurusu'
                                f' rolü {user_major}. Lütfen rol verebilirsin mesajını bekleyiniz.')

                    else:
                        await ctx.send(f':x: {ctx.author.mention}, lütfen başvuru yaparken bölümünüzü belirtiniz.')
                else:
                    await ctx.send(f':x: {ctx.author.mention}, girdiğiniz mail adresi bir üniversiteye ait değildir,'
                                   f' lütfen üniversite maili giriniz.')
            else:
                await ctx.send(f':warning: {ctx.author.mention}, başvurunuz mevcut. Lütfen mailinize gelen kodu'
                               f' .onayla kod şeklinde bize bildiriniz.')
    else:
        await ctx.send(f':warning: {ctx.author.mention}, lütfen bir mail adresi giriniz.')


@client.command()
async def onayla(ctx, code):
    await ctx.channel.purge(limit=1)
    user_id = ctx.message.author.id
    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)
    if MODERATOR_ROLE.lower() in [x.name.lower() for x in ctx.message.author.roles] or ADMIN_ROLE.lower() in [
        y.name.lower() for y in ctx.message.author.roles]:
        if user_id in email_dict.keys():
            if email_dict[user_id][-1][1] == int(code):
                await ctx.send(f':white_check_mark: {ctx.author.mention}, başarılı bir şekilde onaylandınız. Yetkililer'
                               f' sizi gerekli role atayacaklardır, iyi eğlenceler!')
                await channel.send(f'<@!{str(ADMINS_USER_ID)}> | {ctx.author.mention}\'nin üniversite başvurusu'
                                   f' onaylanmıştır. Rol verebilirsiniz.')
            else:
                await ctx.send(':x: Girmiş olduğunuz kod hatalı, lütfen kontrol edip bir daha deneyiniz.')
        else:
            await ctx.send(':warning: Başvurunuz bulunamadı, lütfen .basvuru mail yazarak bir başvuru yapınız.')

    else:
        if user_id in email_dict.keys():
            if email_dict[user_id][1] == int(code):
                await ctx.send(f':white_check_mark: {ctx.author.mention}, başarılı bir şekilde onaylandınız. Yetkililer'
                               f' sizi gerekli role atayacaklardır, iyi eğlenceler!')
                await channel.send(f'<@!{str(ADMINS_USER_ID)}> | {ctx.author.mention}\'nin üniversite başvurusu'
                                   f' onaylanmıştır. Rol verebilirsiniz.')

            else:
                await ctx.send(':x: Girmiş olduğunuz kod hatalı, lütfen kontrol edip bir daha deneyiniz.')
        else:
            await ctx.send(':warning: Başvurunuz bulunamadı, lütfen .basvuru mail yazarak bir başvuru yapınız.')


@tasks.loop(minutes=1440)
async def save_and_delete_emails():
    global date
    date = datetime.today().strftime('%Y-%m-%d')

    with open('logs/' + date + '.txt', 'w') as f:
        f.write(json.dumps(email_dict))


@client.command()
@commands.has_role(ADMIN_ROLE)
async def kayitlog(ctx):
    channel = await ctx.author.create_dm()
    await channel.send(email_dict)


@client.command()
@commands.has_role(ADMIN_ROLE)
async def kayitsil(ctx, member: discord.Member):
    key = member.id
    channel = client.get_channel(SERVER_LOG_CHANNEL_ID)

    await channel.send(f'{ctx.author.mention} isimli yetkili kayıtsil methodunu çalıştırdı.')

    if key in email_dict.keys():
        await channel.send(f'``` {key, email_dict.get(key)} isimli girdi silindi.```')

        email_dict.pop(key, None)
        await ctx.send(f'{member.mention}\'ın kaydı silindi.')
    else:
        await ctx.send(f'{member.mention} ile ilgili kayıt bulunamadı.')

        await channel.send(f'Bir girdi silinmedi.')


if __name__ == '__main__':
    main()
