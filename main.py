import os
import time
import discord
import modules
import tempfile
import typing as t
from io import BytesIO
from modules import constants
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

intents = discord.Intents.all()

bot = modules.MyBot(command_prefix=constants.COMMAND_PREFIX, intents=intents)
bot.add_cog(modules.MyHelp(bot))

level_meter = modules.LevelMeter()


@bot.event
async def on_ready():
    """ The function that will run when the bot is ready. """

    activity = discord.Activity(type=discord.ActivityType.playing,  # Setting up bot status.
                                name=f" {constants.BOT_NAME} | {constants.COMMAND_PREFIX} ")

    await bot.change_presence(status=discord.Status.online, activity=activity)

    modules.log("info", f"Bot {bot.user} olarak Discord'a bağlandı!")


@bot.event
async def on_member_join(member: discord.Member):
    """ When a new user joins the server, it sends a message on the specified channel. """

    channel = member.guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)

    if member.bot:
        return

    level_meter.new_member(member.id)  # adds new member to level meter

    if channel is not None:
        await channel.send(f"Aramıza yeni biri katıldı. Sunucumuza hoş geldin {member.mention}.")


@bot.event
async def on_member_remove(member: discord.Member):
    """ When a user leaves the server, it sends a message on the specified channel. """

    channel = member.guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)

    if member.bot:
        return

    level_meter.delete_member(member.id)  # removes member from level meter

    if channel is not None:
        await channel.send(f"{member.name} aramızdan ayrıldı. Hoşçakal {member.name}.")


@bot.event
async def on_message(message: discord.Message):
    if not message.author.bot:
        if f"{message.author.id}" not in level_meter.db.datas:
            level_meter.new_member(message.author.id)

        await level_meter.add_exp(message.guild, message.author.id, 10)

    await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction: discord.Reaction, member: discord.Member):
    if member.bot:
        return

    channelID = reaction.message.channel.id

    if channelID == constants.SERVER_SUGGESTION_CHANNEL_ID:
        # If the message channel is the designated recommendation channel, it controls the recommendation votes.
        reaction_count = reaction.count-1
        channel = member.guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)
        guild = reaction.message.guild

        if any(r.emoji == "✅" for r in reaction.message.reactions) or any(r.emoji == "❌" for r in reaction.message.reactions):
            return

        if reaction_count >= constants.SERVER_SUGGESTION_VOTES_APPROVAL or reaction_count >= (modules.botCount(guild)-guild.member_count):
            if str(reaction.emoji) == "👍":
                await reaction.message.add_reaction("✅")

                embed = modules.createEmbed(":information_source: Bilgilendirme", "Bir öneri oylama ile kabul edildi.")
                embed.add_field("Öneren:", reaction.message.embeds[0].fields[0].value)
                embed.add_field("Öneri:", reaction.message.embeds[0].fields[1].value)
                await channel.send(embed=embed)

            elif str(reaction.emoji) == "👎":
                await reaction.message.add_reaction("❌")

                embed = modules.createEmbed(":information_source: Bilgilendirme", "Bir öneri oylama ile red edildi.")
                embed.add_field("Öneren:", reaction.message.embeds[0].fields[0].value)
                embed.add_field("Öneri:", reaction.message.embeds[0].fields[1].value)
                await channel.send(embed=embed)


@bot.event
async def on_reaction_remove(reaction: discord.Reaction, member: discord.Member):
    if member.bot:
        return

    channelID = reaction.message.channel.id

    if channelID == constants.SERVER_SUGGESTION_CHANNEL_ID:
        # If the message channel is the designated recommendation channel, it controls the recommendation votes.
        reaction_count = reaction.count-1
        channel = member.guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)
        guild = reaction.message.guild

        if any(r.emoji == "✅" for r in reaction.message.reactions) or any(r.emoji == "❌" for r in reaction.message.reactions):
            return

        if reaction_count >= constants.SERVER_SUGGESTION_VOTES_APPROVAL or reaction_count >= (modules.botCount(guild)-guild.member_count):
            if str(reaction.emoji) == "👍":
                await reaction.message.add_reaction("✅")

                embed = modules.createEmbed(":information_source: Bilgilendirme", "Bir öneri oylama ile kabul edildi.")
                embed.add_field("Öneren:", reaction.message.embeds[0].fields[0].value)
                embed.add_field("Öneri:", reaction.message.embeds[0].fields[1].value)
                await channel.send(embed=embed)

            elif str(reaction.emoji) == "👎":
                await reaction.message.add_reaction("❌")

                embed = modules.createEmbed(":information_source: Bilgilendirme", "Bir öneri oylama ile red edildi.")
                embed.add_field("Öneren:", reaction.message.embeds[0].fields[0].value)
                embed.add_field("Öneri:", reaction.message.embeds[0].fields[1].value)
                await channel.send(embed=embed)


@bot.event
async def on_command_error(ctx: commands.Context, error):
    """ Sends a message to the user when an error is encountered. """

    if isinstance(error, commands.MissingAnyRole):
        embed = modules.createEmbed(":x: İşlem Başarısız", "Bunu yapmaya yetkiniz yok.")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = modules.createEmbed(":x: İşlem Başarısız", "Lütfen gerekli Paremetreleri girin.\nYardım için \"`help`\" komutunu girin.")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandNotFound):
        embed = modules.createEmbed(":x: İşlem Başarısız", "Bilinmeyen bir komut girdiniz.\nYardım için \"`help`\" komutunu girin.")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MemberNotFound):
        embed = modules.createEmbed(":x: İşlem Başarısız", "Kullanıcı bulunamadı.")
        await ctx.send(embed=embed)

    else:
        embed = modules.createEmbed(":x: İşlem Başarısız", "Bir hata oluştu.")
        embed.add_field("Hata:", f"{str(error)}")
        embed.add_field(":information_source: Bilgilendirme", "Hata yetkili kişilere bildirildi.")
        await ctx.send(embed=embed)

        channel = discord.utils.get(ctx.guild.channels, id=constants.SERVER_LOG_CHANNEL_ID)
        admin_role = discord.utils.get(ctx.guild.roles, name=constants.ADMIN_ROLE)
        mod_role = discord.utils.get(ctx.guild.roles, name=constants.MODERATOR_ROLE)
        if channel is not None:
            err_embed = modules.createEmbed(":warning: Bir Hata Oluştu",
                                            f"Komutu Giren: {ctx.author.mention}\nKomut: {ctx.command.name}\nHata: {str(error)}\nHata Sınıfı: {error.__class__.__name__}")
            err_embed.addFooterField = False
            await channel.send(f"{admin_role.mention} {mod_role.mention}", embed=err_embed)

        modules.log("error", error)


@bot.command(name="log", help="Girilen metni konsolda gösterir.", roles=[constants.ADMIN_ROLE])
async def bot_log(ctx: commands.Context, *metin: str):
    """ Displays the entered text on the console. """

    text = " ".join(metin)
    await ctx.message.delete()
    modules.log("info", text)


@bot.command(name="log_message", help="\"message\" değişkenini konsolda gösterir.", roles=[constants.ADMIN_ROLE])
async def log_message(ctx: commands.Context):
    """ Displays the message variable in the console. """

    await ctx.message.delete()
    modules.log("info", ctx.message)


@bot.command(name="bot_mesaj", aliases=["b_m"], help="Bot ile mesaj göndermek için.", roles=[constants.ADMIN_ROLE])
async def bot_message(ctx: commands.Context, channel: t.Optional[discord.TextChannel], *content: str):
    """ To send a message with the bot. """

    content = " ".join(content)

    await ctx.message.delete()

    if channel is None:
        channel = ctx.channel

    await channel.send(content)


@bot.command(name="bot_embed_mesaj", aliases=["b_e_m"], help="Bot ile embed mesaj göndermek için.", roles=[constants.ADMIN_ROLE])
async def bot_embed_message(ctx: commands.Context, channel: t.Optional[discord.TextChannel]):
    """ To send embed messages with bot. """

    embed_data = modules.loadJsonFile("datas/embed.json")

    embed = modules.createEmbed(embed_data["options"]["title"], embed_data["options"]["description"])

    for field in embed_data:
        if field == "options":
            continue

        embed.add_field(field, embed_data[field][0], embed_data[field][1])

    await ctx.message.delete()

    if channel is None:
        channel = ctx.channel

    await channel.send(embed=embed)


@bot.command(name="bot_duyuru", aliases=["b_d"], help="Bot ile duyuru yayınlamak için.", roles=[constants.ADMIN_ROLE])
async def bot_duyuru(ctx: commands.Context, mentione_everyone: t.Optional[bool] = False, *content: str):
    """ To post an announcement with the bot. """

    channel = ctx.guild.get_channel(constants.SERVER_ANNOUNCEMENT_CHANNEL_ID)

    if channel is None:
        return

    content = " ".join(content)

    await ctx.message.delete()

    if mentione_everyone:
        await channel.send(f"{content}\n@everyone")
    else:
        await channel.send(content)


@bot.command(name="bot_embed_duyuru", aliases=["b_e_d"], help="Bot ile embed duyuru yayınlamak için.", roles=[constants.ADMIN_ROLE])
async def bot_embed_duyuru(ctx: commands.Context, mentione_everyone: t.Optional[bool] = False):
    """ To post an embed announcement with the bot. """

    channel: discord.TextChannel = ctx.guild.get_channel(constants.SERVER_ANNOUNCEMENT_CHANNEL_ID)

    if channel is None:
        return

    embed_data = modules.loadJsonFile("datas/embed.json")
    fields = embed_data["fields"]

    embed = modules.createEmbed(embed_data["options"]["title"], embed_data["options"]["description"])

    for field in fields:
        inline = field["inline"] if "inline" in field else None
        embed.add_field(field["name"], field["value"], inline)

    await ctx.message.delete()

    if mentione_everyone:
        await channel.send("@everyone", embed=embed)
    else:
        await channel.send(embed=embed)


@bot.command(name="bot_dm", aliases=["b_dm"], help="Bot ile DM göndermek için.", roles=[constants.ADMIN_ROLE])
async def bot_dm(ctx: commands.Context, member: discord.Member, *content: str):
    """ To send DM with bot. """

    content = " ".join(content)

    content += f"\n\n```NOT: {constants.BOT_NAME}'a Atılan Mesajlar Bize Ulaşmamaktadır.```"

    await ctx.message.delete()

    await member.create_dm()

    await member.dm_channel.send(content)


@bot.command(name="başvuru_listesi", help="Onay bekleyen üniversite rolü başvurularını listeler.", roles=[constants.ADMIN_ROLE, constants.MODERATOR_ROLE])
async def basvuru_list(ctx: commands.Context):
    """ Lists pending university role applications. """

    applications = modules.loadDataFiles("datas/applications")
    channel = ctx.guild.get_channel(constants.SERVER_LOG_CHANNEL_ID)

    await ctx.message.delete()

    msg = ":information_source: Bekleyen Başvurular:"

    if len(applications) <= 0:
        await channel.send("Şuanda onay bekleyen başvuru bulunmamakta.")
    else:
        for application in applications:
            member = discord.utils.get(ctx.guild.members, id=application)
            msg += f"\nKullanıcı: {member.mention} Onay Kodu: {applications[application][3]}"

        await channel.send(msg)


@bot.command(name="mesaj_sayısı", aliases=["message_count"], help="Metin kanalındaki toplam mesaj sayısını döndürür.", roles=[constants.ADMIN_ROLE, constants.MODERATOR_ROLE])
async def message_count(ctx: commands.Context, channel: t.Optional[discord.TextChannel]):
    """ Returns the total number of messages in the text channel. """

    if channel is None:
        channel = ctx.channel
    
    messages = []

    async for message in channel.history(limit=None):
        messages.append(message)

    await ctx.send(f"Bu kanalda toplam {len(messages)} mesaj bulunuyor.")


@bot.command(name="temizle", aliases=["clear", "c"], help="Metin kanalını temizler.", roles=[constants.ADMIN_ROLE, constants.MODERATOR_ROLE])
async def clear(ctx: commands.Context, channel: t.Optional[discord.TextChannel], limit=100):
    """ Clears the text channel. """

    if channel is None:
        channel = ctx.channel
    
    messages = []

    async for message in channel.history(limit=int(limit)):
        messages.append(message)

    await channel.delete_messages(messages)
    await ctx.send(f"Toplam {len(messages)} mesaj temizlendi.", delete_after=5)


@bot.command(name="ban", aliases=["yasakla"], help="Bir kullanıcıyı sunucudan yasaklama.", roles=[constants.ADMIN_ROLE, constants.MODERATOR_ROLE], channels=[constants.SERVER_BOT_COMMAND_CHANNEL])
async def ban(ctx: commands.Context, member: discord.Member, *, sebep=None):
    """ Ban a user from the server. """

    await member.ban(reason=sebep)
    await ctx.send(f"{member.mention} sunucudan banlandı.")


@bot.command(name="unban", aliases=["yasak_kaldır"], help="Bir kullanıcının sunucudaki yasağını kaldırın.", roles=[constants.ADMIN_ROLE, constants.MODERATOR_ROLE], channels=[constants.SERVER_BOT_COMMAND_CHANNEL])
async def unban(ctx: commands.Context, *, member):
    """ Unban a user from the server. """

    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} kullanıcısının sunucu banı kaldırıldı.")
            return

    raise commands.MemberNotFound(member)


@bot.command(name="kick", aliases=["at"], help="Bir kullanıcıyı sunucudan atın.", roles=[constants.ADMIN_ROLE, constants.MODERATOR_ROLE], channels=[constants.SERVER_BOT_COMMAND_CHANNEL])
async def kick(ctx: commands.Context, member: discord.Member, *, sebep=None):
    """ Kick a user from the server. """

    await member.kick(reason=sebep)
    await ctx.send(f"{member.mention} sunucudan atıldı.")


@bot.command(name="selam_ver", help="Mesajı gönderen kişiyi ya da etiketlenen kişiyi selamlar.", channels=[constants.SERVER_BOT_COMMAND_CHANNEL])
async def selam_ver(ctx: commands.Context, member: t.Optional[discord.Member]):
    """ Greets the person who sent the message or the person tagged. """

    if member is None:
        member = ctx.author

    await ctx.message.delete()

    text = f":heart_eyes: :heart_eyes: :heart_eyes:\nSelaaammm {member.mention}"

    await ctx.send(text)


@bot.command(name="öneri", help="Öneri kanalında bir öneri oylaması başlatın.", channels=[constants.SERVER_BOT_COMMAND_CHANNEL])
async def suggestion_f(ctx: commands.Context, *suggestion: str):
    """ Start a suggestion vote in the suggestion channel. """

    suggestion = " ".join(suggestion)
    channel = ctx.guild.get_channel(constants.SERVER_SUGGESTION_CHANNEL_ID)

    if suggestion == "":
        embed = modules.createEmbed(":x: İşlem Başarısız", "Lütfen bir öneri girin.")
        await ctx.send(embed=embed)
        return

    await ctx.message.delete()

    if channel is None:
        return

    embed = modules.createEmbed(":information_source: Bilgilendirme", "Yeni Öneri")
    embed.add_field("Öneren:", ctx.author.mention)
    embed.add_field("Öneri:", suggestion)

    msg = await channel.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")


@bot.command(name="başvuru", help="Üniversite rolü için başvurun.", channels=[constants.SERVER_APPLICATIONS_CHANNEL_ID])
async def basvuru(ctx: commands.Context, email: str, university: str, department: str, member: t.Optional[discord.Member]):
    """ Apply for the university role. """

    if member is None:
        member = ctx.author

    applications = modules.loadDataFiles("datas/applications")

    userID, userName = member.id, member.name

    verificationCode = modules.generateRandomCode()  # generate random verifaction code

    if modules.hasAynRole(member, constants.UNIVERSITY_ROLE):
        embed = modules.createEmbed(":x: İşlem Başarısız", f"{member.mention} | Zaten \"üniversiteli\" rolünüz bulunmakta.")
        await ctx.send(embed=embed)
        return

    if userID in applications:
        embed = modules.createEmbed(":x: İşlem Başarısız", f"{member.mention} | Zaten bir başvurunuz bulunmakta, lütfen <#${constants.SERVER_APPLICATIONS_CHANNEL_ID}> kanalında \"başvuru_onay\" komutu ile onaylayın.\nEğer başvuru ile ilgili bir sıkıntı yaşıyorsanız lütfen Yetkililer ile iletişime geçin.")
        await ctx.send(embed=embed)
        return

    if not modules.validateUniversityEmail(email):
        embed = modules.createEmbed(":x: İşlem Başarısız", f"{member.mention} | Lütfen geçerli bir üniversite e-posta adresi girin.\nEğer başvuru ile ilgili bir sıkıntı yaşıyorsanız lütfen Yetkililer ile iletişime geçin.")
        await ctx.send(embed=embed)
        return

    for application in applications:
        if email == applications[application][0]:
            embed = modules.createEmbed(":x: İşlem Başarısız", f"{member.mention} | Bu email adresi ile daha önce başvuru yapılmış.\nEğer başvuru ile ilgili bir sıkıntı yaşıyorsanız lütfen Yetkililer ile iletişime geçin.")
            await ctx.send(embed=embed)
            return

    await ctx.message.delete()

    modules.sendVerifactionEmail(userName, email, verificationCode)

    applications[userID] = [email, university, department, verificationCode]
    modules.dumpDataFiles("datas/applications", applications)

    embed = modules.createEmbed(":white_check_mark: İşlem Başarılı", f"{member.mention} | Üniversite rolü başvurunuz alınmıştır, lütfen e-posta adresinizi kontrol ediniz.\nEğer başvurunuz iptal etmek istiyorsanız lütfen etkili biri ile iletişime geçin.")
    await ctx.send(embed=embed)


@bot.command(name="başvuru_doğrula", help="Üniversite rolü başvurunuzu doğrulayın.", channels=[constants.SERVER_APPLICATIONS_CHANNEL_ID])
async def basvuru_dogrula(ctx: commands.Context, verifaction_code: str, member: t.Optional[discord.Member]):
    """ Verify your university role application. """

    if member is None:
        member = ctx.author

    modRole = discord.utils.get(ctx.guild.roles, name=constants.MODERATOR_ROLE)

    applications = modules.loadDataFiles("datas/applications")
    channel = ctx.guild.get_channel(constants.SERVER_LOG_CHANNEL_ID)

    userID = member.id

    if userID not in applications:
        embed = modules.createEmbed(":x: İşlem Başarısız", f"{member.mention} | Başvurunuz bulunamadı, lütfen önce <#${constants.SERVER_APPLICATIONS_CHANNEL_ID}> kanalında \"başvuru\" komutu ile başvuruda bulunun.")
        await ctx.send(embed=embed)
        return

    if applications[userID][3] != verifaction_code:
        embed = modules.createEmbed(":x: İşlem Başarısız", f"{member.mention} | Girdiğiniz kod hatalı, lütfen tekrar deneyiniz.")
        await ctx.send(embed=embed)
        return

    await ctx.message.delete()

    embed = modules.createEmbed(":white_check_mark: İşlem Başarılı", f"{member.mention} | Başvurunuz onaylanmıştır. Lütfen bir yetkilinin rolünüzü vermesini bekleyin.")
    await ctx.send(embed=embed)

    embed = modules.createEmbed(":warning: Üniversite Rolü Başvurusu Onaylandı", f"Başvuran: {member.mention}\nE-Posta Adresi: {applications[userID][0]}\nÜniversite: {applications[userID][1]}\nBölümü: {applications[userID][2]}\nLütfen kullanıcının rölünün verin.\n{modRole.mention}")
    await channel.send(embed=embed)

    del applications[userID]
    modules.dumpDataFiles("datas/applications", applications)


@bot.command(name="başvuru_iptal", help="Üniversite rolü başvurunuzu iptal edin.", roles=[constants.ADMIN_ROLE, constants.MODERATOR_ROLE], channels=[constants.SERVER_APPLICATIONS_CHANNEL_ID])
async def basvuru_ıptal(ctx: commands.Context, member: t.Optional[discord.Member]):
    """ Cancel your university role application. """

    if member is None:
        member = ctx.author

    applications = modules.loadDataFiles("datas/applications")

    userID = member.id

    if userID not in applications:
        embed = modules.createEmbed(":x: İşlem Başarısız", f"{member.mention} | Başvurunuz bulunamadı, lütfen önce <#${constants.SERVER_APPLICATIONS_CHANNEL_ID}> kanalında \"başvuru\" komutu ile başvuruda bulunun.")
        await ctx.send(embed=embed)
        return

    await ctx.message.delete()

    embed = modules.createEmbed(":white_check_mark: İşlem Başarılı", f"{member.mention} | Başvurunuz iptal edilmiştir.")
    await ctx.send(embed=embed)

    del applications[userID]
    modules.dumpDataFiles("datas/applications", applications)


@bot.command(name="rol_kaldır", help="Kullanıcıdan bir rolü kaldırır.", roles=[constants.ADMIN_ROLE, constants.MODERATOR_ROLE], channels=[constants.SERVER_BOT_COMMAND_CHANNEL])
async def rol_kaldırma(ctx: commands.Context, role: discord.Role, member: t.Optional[discord.Member]):
    """ Removes a role from the user. """

    await ctx.message.delete()

    if not modules.hasAynRole(member, role.name):
        embed = modules.createEmbed(":x: İşlem Başarısız", "Kullanıcı zaten bu role sahip değil.")
        await ctx.send(embed=embed)
        return
    else:
        await member.remove_roles(role)

        embed = modules.createEmbed(":white_check_mark: İşlem Başarılı", f"{role.name} rolü kullanıcıdan kaldırıldı.")
        await ctx.send(embed=embed)
        return


@bot.command(name="compiler", aliases=["comp", "derleyici"], help="Desteklenen dillerdeki gönderilen kod dosyalarını derler ve çıktıyı mesaj olarak gönderir.", roles=[constants.ADMIN_ROLE, constants.MODERATOR_ROLE, constants.DEVELOPER_ROLE], channels=[constants.SERVER_BOT_COMMAND_CHANNEL])
async def compiler(ctx: commands.Context, file: t.Optional[t.Any], lang: str = "python3"):
    """ It compiles the submitted code files in supported languages and sends the output as a message. """

    supported_langs = ["python3", "python2", "cpp", "c++", "c"]
    compiler_file = tempfile.NamedTemporaryFile(delete=False)  # create new temp file
    compiler_error = None
    output = None

    if lang not in supported_langs:  # check if language supported
        embed = modules.createEmbed(":x: İşlem Başarısız", "Desteklenmeyen bir programlama dili girdiniz.")
        supported_langs_str = f"\n• {supported_langs[0]}"
        for spl in supported_langs[1:]:
            supported_langs_str += f"\n• {spl}"
        embed.add_field("Desteklenen Diller:", supported_langs_str, inline=False)

        await ctx.send(embed=embed)
        return

    if len(ctx.message.attachments) > 1:
        embed = modules.createEmbed(":x: İşlem Başarısız", "Birden fazla dosya derlenememekte, lütfen yanlızca bir dosya yükleyiniz.")
        await ctx.send(embed=embed)
        return
    elif len(ctx.message.attachments) == 1:
        file = ctx.message.attachments[0]
        compiler_file.write(await file.read())
    elif len(ctx.message.attachments) == 0:
        embed = modules.createEmbed(":x: İşlem Başarısız", "Lütfen kod dosyanızı yükleyin.")
        await ctx.send(embed=embed)
        return

    compiler_file.close()

    embed = modules.createEmbed(":warning: Bilgilendirme", "Kodunuz derleniyor...")

    msg = await ctx.send(embed=embed)

    time.sleep(2)

    try:  # compiles the file
        if lang == "python3":
            output, compiler_error = modules.executeShellCommand(f"python3 {compiler_file.name}")
        elif lang == "python2":
            output, compiler_error = modules.executeShellCommand(f"python2 {compiler_file.name}")
        elif lang == "cpp" or lang == "c++":
            __, __ = modules.executeShellCommand(f"mv {compiler_file.name} {compiler_file.name}.cpp")
            compiler_file.name = f"{compiler_file.name}.cpp"
            __, compiler_error = modules.executeShellCommand(f"g++ {compiler_file.name} -o {compiler_file.name}.cpp_o")
            
            if compiler_error is not None:
                await msg.delete()

                embed = modules.createEmbed(":x: İşlem Başarısız", "Kodunuz derlenirken bir hata oluştu.")
                embed.add_field("Programlama Dili:", lang)
                embed.add_field("Dosya:", file.filename)
                embed.add_field("Hata:", f"`{compiler_error}`")
                await ctx.send(embed=embed)
                return

            output, compiler_error = modules.executeShellCommand(f"{compiler_file.name}.cpp_o")
            modules.executeShellCommand(f"rm {compiler_file.name}.cpp_o")
        elif lang == "c":
            __, __ = modules.executeShellCommand(f"mv {compiler_file.name} {compiler_file.name}.c")
            compiler_file.name = f"{compiler_file.name}.c"
            __, compiler_error = modules.executeShellCommand(f"gcc {compiler_file.name} -o {compiler_file.name}.c_o")
            
            if compiler_error is not None:
                await msg.delete()
                
                embed = modules.createEmbed(":x: İşlem Başarısız", "Kodunuz derlenirken bir hata oluştu.")
                embed.add_field("Programlama Dili:", lang)
                embed.add_field("Dosya:", file.filename)
                embed.add_field("Hata:", f"`{compiler_error}`")
                await ctx.send(embed=embed)
                return

            output, compiler_error = modules.executeShellCommand(f"{compiler_file.name}.c_o")
            modules.executeShellCommand(f"rm {compiler_file.name}.c_o")
    finally:
        os.unlink(compiler_file.name)

    if compiler_error is None:
        await msg.delete()

        embed = modules.createEmbed(":white_check_mark: İşlem Başarılı", "Kodunuz derlendi.")
        embed.add_field("Programlama Dili:", lang)
        embed.add_field("Dosya:", file.filename)
        embed.add_field("Çıktı:", f"`{output}`")
        await ctx.send(embed=embed)
    else:
        await msg.delete()

        embed = modules.createEmbed(":x: İşlem Başarısız", "Kodunuz derlenirken bir hata oluştu.")
        embed.add_field("Programlama Dili:", lang)
        embed.add_field("Dosya:", file.filename)
        embed.add_field("Hata:", f"`{compiler_error}`")
        await ctx.send(embed=embed)


@bot.command(name="profil", aliases=["profile", "p"], help="Kullanıcının profilini gösterir.", channels=[constants.SERVER_BOT_COMMAND_CHANNEL])
async def profile(ctx: commands.Context, member: discord.Member = None):
    """ Displays the user's profile. """

    if member is None:
        member: discord.Member = ctx.author

    name, nick, ID, status = str(member), member.display_name, str(member.id), str(member.status)

    status = status.replace("online", "Çevrimiçi").replace("offline", "Çevrimdışı").replace("idle", "Boşta")
    status = status.replace("dnd", "Rahatsız Etmeyin").replace("do_not_disturb¶", "Rahatsız Etmeyin").replace("invisible", "Görünmez")

    if member.bot:
        exp, level = "-", "-"
    else:
        exp, level = f"{level_meter.get_member_exp(member.id)}/{level_meter.get_member_next_level_requirements(member.id)}", f"{level_meter.get_member_level(member.id)}"

    created_at = modules.strftimeTranslate(member.created_at.strftime("%-d %b %Y"))
    joined_at = modules.strftimeTranslate(member.joined_at.strftime("%-d %b %Y"))

    pfp = member.guild_avatar.with_size(256) if member.guild_avatar is not None else member.avatar.with_size(256)  # get member avatar
    pfp_data = BytesIO(await pfp.read())
    pfp: Image.Image = Image.open(pfp_data).convert("RGBA")
    pfp = modules.getCircledImage(pfp)

    guild_banner = None
    guild_icon = None

    if ctx.guild.banner is not None:  # get guild banner if is not None
        guild_banner = ctx.guild.banner.with_size(256)
        guild_banner_data = BytesIO(await guild_banner.read())
        guild_banner: Image.Image = Image.open(guild_banner_data).convert("RGBA")
        guild_banner = guild_banner.resize((230, 230), Image.ANTIALIAS)

    guild_icon = ctx.guild.icon.with_size(256)  # get guild icon
    guild_icon_data = BytesIO(await guild_icon.read())
    guild_icon: Image.Image = Image.open(guild_icon_data).convert("RGBA")
    guild_icon = guild_icon.resize((230, 230), Image.ANTIALIAS)

    base: Image.Image = Image.open("datas/assets/ProfieUI/base.png").convert("RGBA")  # open base image
    bg: Image.Image = Image.open("datas/assets/ProfieUI/white_background.png").convert("RGBA")  # open background image

    name = f"{name[:14]}.." if len(name) > 16 else name  # if name len long than 16 resize name
    nick = f"{nick[:15]}.." if len(nick) > 17 else nick  # if nick len long than 17 resize nick

    # load fonts
    font = ImageFont.truetype("datas/assets/ProfieUI/Roboto-Bold.ttf", 38)
    nick_font = ImageFont.truetype("datas/assets/ProfieUI/Roboto-Bold.ttf", 30)
    sub_font = ImageFont.truetype("datas/assets/ProfieUI/Roboto-Bold.ttf", 25)

    # draw text on image
    draw = ImageDraw.Draw(base)
    draw.text((280, 240), name, font=font)
    draw.text((270, 315), nick, font=nick_font)
    draw.text((65, 490), ID, font=sub_font)
    draw.text((405, 490), status, font=sub_font)
    draw.text((65, 635), exp, font=sub_font)
    draw.text((405, 635), level, font=sub_font)
    draw.text((65, 785), created_at, font=sub_font)
    draw.text((405, 785), joined_at, font=sub_font)
    base.paste(pfp, (56, 158), pfp)

    if guild_banner is not None:
        bg.paste(guild_banner, (0, 0), guild_banner)
    else:
        bg.paste(guild_icon, (int(bg.size[0]/2-guild_icon.size[0]/2), 0), guild_icon)

    bg.paste(base, (0, 0), base)

    # save image to BytesIO and send image to channel
    with BytesIO() as fp:
        bg.save(fp, "PNG")
        fp.seek(0)
        await ctx.send(file=discord.File(fp, "profil.png"))


@bot.command(name="sunucu", aliases=["server", "s"], help="Sunucu bilgisini gösterir.", channels=[constants.SERVER_BOT_COMMAND_CHANNEL])
async def server(ctx: commands.Context):
    """ Shows server information. """

    show_members = True
    guild = ctx.guild
    owner = await guild.fetch_member(guild.owner_id)
    name, ID, owner, member_count, channel_count = guild.name, str(guild.id), str(owner.name), str(guild.member_count-modules.botCount(guild)), str(len(guild.channels))
    created_at = modules.strftimeTranslate(guild.created_at.strftime("%-d %b %Y"))

    online_members = 0
    offline_members = 0

    for member in guild.members:
        if str(member.status) in ["online", "idle", "dnd", "do_not_disturb"]:
            if not member.bot:
                online_members += 1
        else:
            if not member.bot:
                offline_members += 1

    members = f"Çevrimiçi: {online_members}   Bot: {modules.botCount(guild)}\n       Çevrimdışı: {offline_members}"

    guild_banner = None
    guild_icon = None

    if ctx.guild.banner is not None:  # get guild banner if is not None
        guild_banner = ctx.guild.banner.with_size(256)
        guild_banner_data = BytesIO(await guild_banner.read())
        guild_banner: Image.Image = Image.open(guild_banner_data).convert("RGBA")
        guild_banner = guild_banner.resize((230, 230), Image.ANTIALIAS)

    guild_icon = ctx.guild.icon.with_size(256)  # get guild icon
    guild_icon_data = BytesIO(await guild_icon.read())
    guild_icon: Image.Image = Image.open(guild_icon_data).convert("RGBA")

    pfp = modules.getCircledImage(guild_icon)

    guild_icon = guild_icon.resize((230, 230), Image.ANTIALIAS)

    # open base image
    if show_members:
        base: Image.Image = Image.open("datas/assets/ServerUI/base2.png").convert("RGBA")
    else:
        base: Image.Image = Image.open("datas/assets/ServerUI/base.png").convert("RGBA")

    bg: Image.Image = Image.open("datas/assets/ServerUI/white_background.png").convert("RGBA")  # open background image

    name = f"{name[:14]}.." if len(name) > 16 else name  # if name len long than 16 resize name

    # load fonts
    font = ImageFont.truetype("datas/assets/ServerUI/Roboto-Bold.ttf", 38)
    sub_font = ImageFont.truetype("datas/assets/ServerUI/Roboto-Bold.ttf", 25)

    # draw text on image
    draw = ImageDraw.Draw(base)
    draw.text((280, 240), name, font=font)
    draw.text((65, 490), ID, font=sub_font)
    draw.text((405, 490), owner, font=sub_font)
    draw.text((65, 635), member_count, font=sub_font)
    draw.text((405, 635), channel_count, font=sub_font)

    if show_members:
        draw.text((65, 785), created_at, font=sub_font)
        draw.text((405, 770), members, font=sub_font)
    else:
        draw.text((240, 785), created_at, font=sub_font)

    base.paste(pfp, (56, 158), pfp)

    if guild_banner is not None:
        bg.paste(guild_banner, (0, 0), guild_banner)
    else:
        bg.paste(guild_icon, (int(bg.size[0]/2-guild_icon.size[0]/2), 0), guild_icon)

    bg.paste(base, (0, 0), base)

    # save image to BytesIO and send image to channel
    with BytesIO() as fp:
        bg.save(fp, "PNG")
        fp.seek(0)
        await ctx.send(file=discord.File(fp, "server.png"))


if __name__ == "__main__":
    bot.run(constants.BOT_TOKEN)
