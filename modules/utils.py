import re
import json
import time
import pickle
import codecs
import random
import modules
import smtplib
import discord
import functools
import subprocess
import typing as t
from modules import constants
from os import path as os_path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageChops, ImageDraw

__all__ = [
    "botCount",
    "createDataFiles",
    "createEmbed",
    "dumpDataFiles",
    "dumpJsonFile",
    "executeShellCommand",
    "generateRandomCode",
    "getCircledImage",
    "hasAynRole",
    "isExists",
    "loadDataFiles",
    "loadJsonFile",
    "log",
    "sendEmail",
    "splitArgString",
    "strftimeTranslate",
    "validateUniversityEmail"
]


def loadDataFiles(filePath: str) -> t.Any:
    """
        Load decoded data files with pickle.

        :param filePath: File path.
        :type filePath: str
        :returns: File datas.
        :rtype: Any
    """
    return pickle.loads(codecs.decode(open(filePath, "rb").read(), "zlib"))


def dumpDataFiles(filePath: str, data: t.Any) -> None:
    """
        Dump encoded data files with pickle.

        :param filePath: File path.
        :param data: File data.
        :type filePath: str
        :type : Any
    """
    open(filePath, "wb").write(codecs.encode(pickle.dumps(data), "zlib"))


def createDataFiles(filePath: str) -> None:
    """
        Create data files with pickle.

        :param filePath: File path.
        :type filePath: str
    """
    open(filePath, "wb").write(codecs.encode(pickle.dumps({}), "zlib"))


def loadJsonFile(filePath: str) -> dict:
    """
        Load json file.

        :param filePath: File path.
        :type filePath: str
        :returns: Json data.
        :rtype: dict
    """
    with open(filePath) as fp:
        data = json.load(fp)
    return data


def dumpJsonFile(filePath: str, data: dict) -> None:
    """
        Dump json data to file.

        :param filePath: File path.
        :param: Json data.
        :type filePath: str
        :type: dict
    """
    with open(filePath, "w") as fp:
        json.dump(data, fp)


def isExists(path: str) -> bool:
    """
        Check if path exists.

        :param path: The path to check.
        :type path: str
        :rtype: bool
    """
    return os_path.exists(path)


def log(level: str, msg: str):
    """
        Print log.

        :param level: Log level.
        :param msg: Log message.
        :type level: str
        :type msg: str
    """
    levels = {"info": "[INFO]", "warning": "[WARNING]", "error": "[ERROR]"}
    print(f"{time.strftime('%d.%m.%YT%H:%M:%S')} :: {levels[level]} {msg}")


def createEmbed(title: str, description: str, colour: int = constants.EMBED_COLOUR) -> modules.MyEmbed:
    """
        Create new embed.

        :param title: Embed title.
        :param description: Embed description.
        :param colour: Embed colour.
        :type title: str
        :type description: str
        :type colour: int
        :returns: New embed.
        :rtype: modules.MyEmbed
    """
    embed = modules.MyEmbed(title=title, description=description, colour=colour)
    embed.set_author(name=constants.EMBED_AUTHOR_NAME, url=constants.EMBED_AUTHOR_URL, icon_url=constants.EMBED_AUTHOR_ICON_URL)
    return embed


def hasAynRole(member: discord.Member, roles: list) -> bool:
    """
        Check if member has any role.

        :param member: Member to check..
        :param roles: Roles to check.
        :type member: discord.Member
        :type roles: list
        :rtype: bool
    """
    if isinstance(roles, str):
        roles = [roles]

    getter = functools.partial(discord.utils.get, member.roles)
    return any(getter(id=role) is not None if isinstance(role, int) else getter(name=role) is not None for role in roles)


def botCount(guild: discord.Guild) -> int:
    """
        Returns the number of bots on the guild.

        :param guild: The guild whose number of bot will be returned.
        :type guild: discord.Guild
        :returns: Bot count.
        :rtype: int
    """
    bot_count = 0

    for member in guild.members:
        if member.bot:
            bot_count += 1

    return bot_count


def strftimeTranslate(txt: str) -> str:
    """
        Translate strftime output to Turkish.

        :param txt: strftime output.
        :type txt: str
        :rtype: str
    """
    b = {"Jan": "Ocak", "Feb": "Şubat", "Mar": "Mart", "Apr": "Nisa", "May": "Mayıs", "Jun": "Haziran", "Jul": "Temmuz", "Aug": "Ağustos", "Sep": "Eylül", "Oct": "Ekim", "Nov": "Kasım", "Dec": "Aralık"}

    for i in b:
        if i in txt:
            txt = txt.replace(i, b[i])

    return txt


def validateUniversityEmail(email: str) -> bool:
    """
        Validates whether the email is a university email or not.

        :param email: Email address.
        :type email: str
        :rtype: bool
    """
    r1 = re.match("\\S+@\\S+\\.edu", email)
    r2 = re.match("\\S+@\\S+\\.edu\\S+", email)

    return (r1 is not None or r2 is not None)


def generateRandomCode(length: int = constants.RANDOM_CODE_LEN, char_set: str = constants.RANDOM_CODE_CHAR_SET) -> str:
    """
        Generate random code.

        :param length: Length of code.
        :param char_set: Char set of code.
        :type length: int
        :type char_set: str
        :returns: Generated code.
        :rtype: str
    """
    return "".join(random.choices(char_set, k=length))


def getCircledImage(im: Image.Image, size=(215, 215)) -> Image.Image:
    """
        Rearranges the image in a circle.

        :param im: The image to be edited.
        :param size: New image size.
        :type im: Image.Image
        :type size: tuple
        :returns: New image.
        :rtype: Image.Image
    """
    im = im.resize(size, Image.ANTIALIAS)
    big_size = (im.size[0]*3, im.size[1]*3)
    mask = Image.new("L", big_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0)+big_size, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)
    return im


def splitArgString(arg_s: str) -> list:
    """
        Splits string of arguments.

        :param arg_s: String of arguments.
        :type arg_s: str
        :returns: List of arguments.
        :rtype: list
    """
    rv = []
    for match in re.finditer(r"('([^'\\]*(?:\\.[^'\\]*)*)'"
                             r'|"([^"\\]*(?:\\.[^"\\]*)*)"'
                             r'|\S+)\s*', arg_s, re.S):
        arg = match.group().strip()
        if arg[:1] == arg[-1:] and arg[:1] in '"\'':
            arg = arg[1:-1].encode("ascii", "backslashreplace") \
                .decode("unicode-escape")
        try:
            arg = type(arg_s)(arg)
        except UnicodeError:
            pass
        rv.append(arg)
    return rv


def executeShellCommand(command: t.Union[str, list], decode: bool = True, decoding: str = "utf-8") -> t.Tuple[str, t.Union[str, None]]:
    """
        Execute shell command.

        :param command: Command.
        :param decode: Decode the output.
        :param decoding: Decoding format.
        :type command: t.Union[str, list]
        :type decode: bool
        :type decoding: str
        :returns: Output and error.
        :rtype: t.Tuple[str, t.Union[str, None]]
    """
    if isinstance(command, str):
        command_args = splitArgString(command)
    else:
        command_args = command

    p = subprocess.Popen(command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    output = p[0]
    error = None

    if len(p[1]) > 0:
        error = p[1]

    if decode:
        output = output.decode(decoding)
        if error is not None:
            error = error.decode(decoding)

    return output, error


def sendEmail(receiver: str, subject: str, content: str):
    """
        Send email.

        :param receiver: Receiver.
        :param subject: E-mail subject.
        :param filePath: E-mail content.
        :type receiver: str
        :type subject: str
        :type content: str
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = constants.SENDEMAIL_FROM
    msg["To"] = receiver

    part1 = MIMEText(content, "plain", "utf-8")
    msg.attach(part1)
    text = msg.as_string().encode("ascii")

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(constants.SENDEMAIL_EMAIL_ADDRESS, constants.SENDEMAIL_EMAIL_PASSWORD)
        server.sendmail(constants.SENDEMAIL_FROM, receiver, text)
        server.close()
    except Exception as e:
        raise modules.errors.SendEmailError(str(e))


def sendVerifactionEmail(name: str, email: str, verifactionCode: str):
    """
        Send verification email.

        :param name: Member name.
        :param email: Member e-mail.
        :param verifactionCode: Verifaction code.
        :type name: str
        :type email: str
        :type verifactionCode: str
    """
    content = f"Merhaba {name},\n\
            Ben {constants.BOT_NAME}, {constants.SERVER_NAME} Discord sunucusunda moderasyonu sağlamakla görevliyim. Kısa bir süre önce bir kullanıcı bu mail adresini kullanarak sunucuda kendisini onaylatmaya çalıştı. \
            Onaylanmayı sen talep etmediysen bu maili görmezden gelebilirsin. Eğer bu işlemi sen gerçekleştirdiysen alt tarafta bulunan komutu universite-rolu-basvurusu odasına yazabilirsin.\n\
            \n\
            .başvuru_onay {verifactionCode}\n\
            \n\
            Not: Bu isteği bir moderatör yardımı ile gerçekleştirdiyseniz bu kodu ona söylemeniz yeterlidir.\n\
            \n\
            İyi eğlenceler!\n\
            {constants.SERVER_NAME} Yönetimi"

    sendEmail(email, f"{constants.SERVER_NAME} Discord | Üniversite Rolü Başvuru Onaylama", content)
