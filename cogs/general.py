from os import name
import discord
import asyncio
import random
import datetime
from discord import user
from discord import channel
from discord import client
from discord.ext.commands import bot
from discord.utils import get
from discord.ext import commands, tasks
import validators
from validators.utils import ValidationFailure


class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("General plugged in.")
        await self.bot.primedb.execute(
            "create table if not exists weatherevents (weather text, description text, url text)"
        )
        print("weatherevent table connected")


    

    @commands.command()
    @commands.has_guild_permissions(mute_members=True)
    async def createweather(self, ctx):
        def is_correct(m):
            return m.author == ctx.author

        draft = await self.bot.primedb.fetch("select weather from weatherevents")
        allevs = [x["weather"] for x in draft]
        print(allevs)

        await ctx.send(
            f"{ctx.author.mention}, what will the name of the weather event be?"
        )
        try:
            wthr = await self.bot.wait_for("message", check=is_correct, timeout=15.0)
            if wthr.content in allevs:
                await ctx.send(
                    f"{ctx.author.mention}, that weather already exists. Try again."
                )
                return

        except asyncio.TimeoutError:
            return await ctx.send(f"Timed out. Please try again.")

        print(f"Name set to `{wthr.content}`.")
        await ctx.send(f" Please enter the description of the weather event.")

        def isurl(url_string: str) -> bool:
            result = validators.url(url_string)

            if isinstance(result, ValidationFailure):
                return False

            return result

        try:
            dscp = await self.bot.wait_for("message", check=is_correct, timeout=15.0)

        except asyncio.TimeoutError:
            return await ctx.send(f"Timed out. Please try again.")

        print(f"desc set to `{dscp.content}`.")
        await ctx.send(f"Please enter URL of image to be displayed for this event.")

        try:
            wurl = await self.bot.wait_for("message", check=is_correct, timeout=15.0)
            if not isurl(wurl.content):
                await ctx.send(
                    f"{ctx.author.mention}, this is not a valid image url. Please try again."
                )
                return

        except asyncio.TimeoutError:
            return await ctx.send(f"Timed out. Please try again.")

        print(f"url set to `{wurl.content}`.")

        if wthr and dscp and wurl:
            report = await self.bot.primedb.fetch(
                "INSERT INTO weatherevents (weather, description, url) VALUES ($1, $2, $3) RETURNING *",
                wthr.content,
                dscp.content,
                wurl.content,
            )
            await ctx.send(f"New weather event added!")
            em = discord.Embed(
                title="Weather Report",
                color=discord.Color.purple(),
                description=f"```{report[0]['description']}```",
            )
            em.set_image(url=report[0]["url"])
            await ctx.send(embed=em)

    @commands.command()
    @commands.has_guild_permissions(mute_members=True)
    async def weather(self, ctx):
        report = await self.bot.primedb.fetch(
            "SELECT * FROM weatherevents ORDER BY RANDOM() LIMIT 1"
        )
        em = discord.Embed(
            title="Weather Report",
            color=discord.Color.purple(),
            description=f"```{report[0]['description']}```",
        )
        em.set_image(url=report[0]["url"])
        await ctx.send(embed=em)

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        em = get_main_help_embed(
            description="Use `p!help` Command for information.",
            picture=self.bot.user.avatar_url,
        )

        em.add_field(
            name="Moderation",
            value=f"``` kick \n ban \n strike \n mute \n unmute \n trackuser \n dump```",
        )
        em.add_field(
            name="Ferin",
            value=f"``` balance \n fleaderboard \n work \n daily \n gamble ```",
        )
        em.add_field(name="Levelling", value=f"``` rank \n leaderboard```", inline=True)

        em.set_footer(text="Primordiax | V2.81 | artixian#7260")

        await ctx.send(embed=em)

    @help.command()
    async def kick(self, ctx):

        em = get_help_embed(
            title="Kick",
            description="Kicks a member from the server.",
            picture=self.bot.user.avatar_url,
        )
        em.add_field(name="**Syntax**", value=f"`p!kick <member> [reason]`")
        await ctx.send(embed=em)

    @help.command()
    async def ban(self, ctx):

        em = get_help_embed(
            title="Ban",
            description="Bans a member from the server.",
            picture=self.bot.user.avatar_url,
        )
        em.add_field(name="**Syntax**", value=f"`p!ban <member> [reason]`")
        await ctx.send(embed=em)

    @help.command()
    async def strike(self, ctx):

        em = get_help_embed(
            title="Strike",
            description="Adds a strike to a user.",
            picture=self.bot.user.avatar_url,
        )
        em.add_field(
            name="**Syntax**",
            value=f"`p!strike <member> [reason]` \n Using `!xp take <member>` will also add a strike to the user.",
        )
        await ctx.send(embed=em)

    @help.command()
    async def mute(self, ctx):
        em = get_help_embed(
            title="Mute",
            description="Mutes and adds a strike to a user.",
            picture=self.bot.user.avatar_url,
        )
        em.add_field(name="**Syntax**", value=f"`p!mute <member> <time> [reason]` \n.")
        await ctx.send(embed=em)

    @help.command()
    async def trackuser(self, ctx):
        em = get_help_embed(
            title="Track",
            description="Tracks a user.",
            picture=self.bot.user.avatar_url,
        )
        em.add_field(name="**Syntax**", value=f"`p!trackuser <member> ` \n.")
        await ctx.send(embed=em)

    @help.command()
    async def leaderboard(self, ctx):

        em = get_help_embed(
            title="Leaderboard",
            description="Displays leaderboard of people with most xp.",
            picture=self.bot.user.avatar_url,
        )
        em.add_field(name="**Syntax**", value=f"`p!leaderboard`")
        await ctx.send(embed=em)

    @help.command()
    async def rank(self, ctx):

        em = get_help_embed(
            title="Rank", description="Displays rank.", picture=self.bot.user.avatar_url
        )
        em.add_field(name="**Syntax**", value=f"`p!rank`")
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(general(bot))


def get_main_help_embed(description, picture):
    title = "Help Menu | Primordiax"
    symbol = "https://i.imgur.com/MSg2a9d.png"
    embed = discord.Embed(description=description, color=7505388)
    embed.set_thumbnail(url=picture)
    embed.set_author(name=title, icon_url=symbol)
    embed.set_footer(text=f"Helpdesk for Primordiax.")
    return embed


def get_help_embed(title, description, picture):
    title = "Help Menu | Primordiax"
    symbol = "https://i.imgur.com/MSg2a9d.png"
    embed = discord.Embed(description=description, color=7505388)
    embed.set_thumbnail(url=picture)
    embed.set_author(name=title, icon_url=symbol)
    embed.set_footer(text=f"Helpdesk for Primordiax.")
    return embed


# Permission check
def check_permissions(roles):
    for scan in roles:
        if scan.name == "Tester":
            return True
    return False
