import json
import pickle
import discord
import modules
import typing as t
from modules import constants
from discord.ext import commands


__all__ = [
    "LevelMeter",
    "MyBot",
    "MyCommand",
    "MyEmbed",
    "MyHelp",
    "Namespace"
]


class Namespace:
    """Simple object for storing attributes.

    Implements equality by attribute names and values, and provides a simple
    string representation.
    """

    def __init__(self, data: dict = None, **kwargs) -> None:
        if data is not None and isinstance(data, dict):
            for name in data:
                self.__setattr__(name, data[name])
        else:
            for name in kwargs:
                self.__setattr__(name, kwargs[name])

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def __eq__(self, other: "Namespace") -> bool:
        if not isinstance(other, Namespace):
            return NotImplemented
        return vars(self) == vars(other)

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        star_args = {}
        for arg in self._get_args():
            arg_strings.append(repr(arg))
        for name, value in self._get_kwargs():
            if name.isidentifier():
                arg_strings.append(f"{name}={value}")
            else:
                star_args[name] = value
        if star_args:
            arg_strings.append(f"**{repr(star_args)}")
        return f"{type_name}({', '.join(arg_strings)})"

    def _get_kwargs(self):
        return sorted(self.__dict__.items())

    def _get_args(self):
        return []

    def get(self, name: str) -> t.Any:
        """Get attributes

        :param name: Attributes name
        :type name: str
        """
        return self.__dict__.get(name, None)

    def getAll(self) -> dict:
        """ Get all attributes """
        return self.__dict__

    def update(self, data: dict = None, **kwargs) -> None:
        """
            Update attributes

            :param data: Attributes dict, defaults to None
            :type data: dict, optional
        """
        if data is not None and isinstance(data, dict):
            for name in data:
                self.__setattr__(name, kwargs[name])

        for name in kwargs:
            self.__setattr__(name, kwargs[name])

    def delete(self, *args, names: list = None) -> None:
        """
            Delete attributes

            :param names: Name list defaults to None
            :type names: list, optional
        """
        if names is not None and (isinstance(names, list) or isinstance(names, tuple)):
            for name in names:
                self.__delattr__(name)

        if names is not None and isinstance(names, str):
            self.__delattr__(names)

    def keys(self) -> list:
        """
            Return attributes keys

            :return: Attributes keys
            :rtype: list
        """
        return list(self.__dict__.keys())

    @classmethod
    def from_json_file(cls, filePath: str) -> "Namespace":
        """
            Load object from json file

            :param filePath: File path.
            :type filePath: str
            :return: Object loaded from json file.
            :rtype: Namespace
        """
        with open(filePath) as fp:
            data = json.load(fp)
        return cls(data=data)

    def dump(self) -> bytes:
        """
            Dump object to data

            :return: Dumped data
            :rtype: bytes
        """
        return pickle.dumps(self)

    @staticmethod
    def load(data: bytes) -> t.Any:
        """
            Load object from data

            :param data: Data to load the object
            :type data: bytes
            :return: Object loaded from data
            :rtype: t.Any
        """
        return pickle.loads(data)


class MyBot(commands.Bot):
    def command(self, *args, **kwargs):
        def decorator(func):
            kwargs.setdefault('parent', self)

            if "cls" not in kwargs:
                kwargs.setdefault('cls', MyCommand)

            result = commands.command(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator

    async def process_commands(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if ctx.command is not None:
            channels = ctx.command.channels

            for channel in channels:
                if isinstance(channel, str):
                    channels.append(int(channel))

            if message.channel.id not in channels and len(channels) > 0:
                return

            roles = ctx.command.roles
            if not modules.hasAynRole(message.author, roles) and len(roles) > 0:
                raise commands.MissingAnyRole(roles)

        await self.invoke(ctx)


class MyCommand(commands.Command):
    def __init__(self, func, **kwargs):
        self.roles = kwargs.get("roles", [])
        self.channels = kwargs.get("channels", [])
        super().__init__(func, **kwargs)


class MyEmbed(discord.Embed):
    def __init__(self, addFooterField: bool = True, **kwargs):
        self.addFooterField = addFooterField
        super().__init__(**kwargs)

    def add_field(self, name: t.Any, value: t.Any, inline: bool = False):
        if inline is  None:
            inline = False
        return super().add_field(name=name, value=value, inline=inline)

    def to_dict(self):
        if self.addFooterField:
            self.add_field(name=constants.EMBED_FOOTER[0], value=constants.EMBED_FOOTER[1], inline=constants.EMBED_FOOTER[2])

        return super().to_dict()


class MyHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")
        self.turkish_keys = {
                                "member": "kullanıcı",
                                "content": "içerik",
                                "channel": "kanal",
                                "mentione_everyone": "herkesten_bahset",
                                "suggestion": "öneri",
                                "university": "üniversite",
                                "department": "bölüm",
                                "verifaction_code": "onay_kodu",
                                "role": "rol"
                            }

    def syntax(self, command: MyCommand) -> str:
        """
            Get command syntax string.

            :param command: Command.
            :type command: MyCommand
            :returns: Command syntax string.
            :rtype: str
        """
        cmd_and_aliases = "|".join([str(command), *command.aliases])
        params = []

        for key, value in command.params.items():
            for tk in self.turkish_keys:  # translate key to Turkish
                if tk in key:
                    key = key.replace(tk, self.turkish_keys[tk])

            if key not in ("self", "ctx"):
                params.append(f"[{key}]" if "NoneType" in str(value) or "Optional" in str(value) else f"<{key}>")

        params = " ".join(params)

        return f"`{cmd_and_aliases} {params}`"

    async def cmd_help(self, ctx: commands.Context, command):
        embed = modules.createEmbed(title=f"`{command}` için yardım",
                                    description=self.syntax(command),
                                    colour=ctx.author.colour
                                    )

        embed.add_field(name="Komut açıklaması", value=command.help)
        await ctx.send(embed=embed)

    @commands.command(cls=MyCommand, name="help", aliases=["h", "yardım", "y"], help="Yardım mesajını gösterir.", channels=[938514102433742978])
    async def show_help(self, ctx: commands.Context, cmd: t.Optional[str]):
        """ Show help message """
        if cmd is None:
            fields = {}
            keys = []

            for entry in list(self.bot.commands):
                roles = entry.roles
                if not modules.hasAynRole(ctx.author, roles) and len(roles) > 0:
                    continue

                # fields[entry.name] = (self.syntax(entry), entry.help or "Açıklama yok")
                fields[entry.name] = (entry.help or "Açıklama yok", self.syntax(entry))
                keys.append(entry.name)

            embed = modules.createEmbed(title="Yardım",
                                        description=f"{constants.SERVER_NAME} yardım menüsü",
                                        colour=ctx.author.colour)
            embed.set_thumbnail(url=ctx.guild.me.avatar.url)

            keys.sort()

            for key in keys:
                name, value = fields[key]
                embed.add_field(name=name, value=value, inline=True)

            await ctx.send(embed=embed)

        else:
            if (command := discord.utils.get(self.bot.commands, name=cmd)):
                await self.cmd_help(ctx, command)

            else:
                embed = modules.createEmbed(":x: İşlem Başarısız", "Böyle bir komut mevcut değil.")
                await ctx.send(embed=embed)


class Database:
    def __init__(self, filePath: str):
        self.filePath = filePath
        if not modules.isExists(filePath):
            modules.createDataFiles(filePath)

    @property
    def datas(self) -> dict:
        """ Returns datas in database file """
        return modules.loadDataFiles(self.filePath)

    @datas.setter
    def datas(self, datas: t.Any):
        """ Change datas in database file """
        modules.dumpDataFiles(self.filePath, datas)

    def get(self, key: str) -> t.Union[t.Any, None]:
        """ Returns any key value if exists else returns None """
        return self.datas.get(key, None)

    def update(self, key: str, value: t.Any):
        """ Update key value """
        datas = self.datas
        datas[key] = value
        
        self.datas = datas

    def delete(self, key:str):
        """ Delete key """
        datas = self.datas

        del datas[key]
        self.datas = datas
        


class LevelMeter:
    def __init__(self):
        self.db = Database("datas/databases/levels.db")
        self.level_requirements = {2: 200, 3: 400, 4: 800, 5: 1600, 6: 3200, 7: 6400, 8: 12800, 9: 25600, 10: 51200}
        self.max_level = 10

    def new_member(self, member_id: int):
        """ Add new member """

        member = Namespace(level=1, exp=0)
        self.db.update(f"{member_id}", member.dump())

    def delete_member(self, member_id: int):
        """ Delete a member """

        self.db.delete(f"{member_id}")

    def get_member_level(self, member_id: int) -> int:
        """ Get member level """

        data = self.db.get(f"{member_id}")

        member = Namespace.load(data)
        return int(member.level)

    def get_member_exp(self, member_id: int) -> int:
        """ Get member exp """

        data = self.db.get(f"{member_id}")

        member = Namespace.load(data)
        return int(member.exp)

    def get_level_requirements(self, level: int) -> t.Union[int, None]:
        """ Get any level requirements """

        return self.level_requirements.get(level, None)

    def get_member_next_level_requirements(self, member_id: int) -> t.Union[int, None]:
        """ Get member next level requirements """

        data = self.db.get(f"{member_id}")

        member = Namespace.load(data)
        return self.level_requirements.get(member.level+1, None)

    def add_exp_without_send(self, member_id: int, amount: int):
        """ Add exp to member without sending message """

        data = self.db.get(f"{member_id}")

        member = Namespace.load(data)
        member.exp += amount

        next_level_requirements = self.get_member_next_level_requirements(member)

        while member.exp >= next_level_requirements:
            member.level += 1
            member.exp -= next_level_requirements

            if member.level == self.max_level:
                break

            next_level_requirements = self.get_member_next_level_requirements(member)

        if member.exp < 0:
            member.exp = 0

        self.db.update(f"{member_id}", member.dump())

    async def add_exp(self, guild: discord.Guild, member_id: int, amount: int):
        """ Add exp to member """

        data = self.db.get(f"{member_id}")

        member = Namespace.load(data)
        member.exp += amount

        old_level = member.level

        next_level_requirements = self.get_member_next_level_requirements(member)

        while next_level_requirements is not None and member.exp >= next_level_requirements:
            member.level += 1
            member.exp -= next_level_requirements

            if member.level == self.max_level:
                break

            next_level_requirements = self.get_member_next_level_requirements(member)

        if old_level != member.level:
            channel = guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)
            guild_member = await guild.fetch_member(member_id)
            if member.level == self.max_level:
                await channel.send(f"{guild_member.mention} maksimum seviyeye ulaştı. Tebrikler {guild_member.mention}.")
            else:
                await channel.send(f"{guild_member.mention} {member.level} seviyesine yükseldi. Tebrikler {guild_member.mention}.")

        if member.exp < 0:
            member.exp = 0

        self.db.update(f"{member_id}", member.dump())

    def remove_exp(self, member_id: int, amount: int):
        """ Remove exp from member """

        data = self.db.get(f"{member_id}")

        member = Namespace.load(data)
        member.exp -= amount

        if member.exp < 0:
            member.exp = 0

        self.db.update(f"{member_id}", member.dump())

    def increase_level(self, member_id: int, amount: int):
        """ Increase member level """

        data = self.db.get(f"{member_id}")

        member = Namespace.load(data)
        member.level += amount

        if member.level > self.max_level:
            member.level = self.max_level

        self.db.update(f"{member_id}", member.dump())

    def decrease_level(self, member_id: int, amount: int):
        """ Decrease member level """

        data = self.db.get(f"{member_id}")

        member = Namespace.load(data)
        member.level -= amount

        if member.level < 0:
            member.level = 0

        self.db.update(f"{member_id}", member.dump())

    def reset_member(self, member_id: int):
        """ Reset member level and exp """

        self.new_member(member_id)
