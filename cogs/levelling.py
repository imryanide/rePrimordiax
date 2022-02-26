import discord
from discord import message
from discord.ext import commands
import time
from prettytable import PrettyTable


class levelling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Levelling plugged in.")
        await self.bot.primedb.execute(
            "create table if not exists userlevels (guildid bigint, userid bigint, level bigint,xp bigint, lastmsg real, unique(userid, guildid))"
        )
        print("userlevels table plugged")

    async def levelup(self, user):
        currentxp = user[0]["xp"]
        currentlevel = user[0]["level"]

        if currentxp > round((6 * (currentlevel**3)) / 5):
            await self.bot.primedb.execute(
                "UPDATE userlevels SET level = $1 WHERE userid = $2 AND guildid = $3",
                currentlevel + 1,
                user[0]["userid"],
                user[0]["guildid"],
            )
            return True
        else:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            memberid = message.author.id
            guildid = message.guild.id

            user = await self.bot.primedb.fetch(
                "SELECT * FROM userlevels WHERE userid = $1 AND guildid = $2",
                memberid,
                guildid,
            )

            if not user:
                print("getting user")
                user = await self.bot.primedb.fetch(
                    "INSERT INTO userlevels (userid, guildid, level, xp, lastmsg) VALUES ($1, $2, $3, $4, $5) RETURNING *",
                    memberid,
                    guildid,
                    1,
                    0,
                    time.time(),
                )
                print("got user")
                print(message.guild.id)
            # user = await self.bot.primedb.fetchrow("SELECT * FROM userlevels WHERE userid = $1 AND guildid = $2", memberid, guildid)

            if not message.content[:2] in ["!p", "p!"] or message.content[0] == "$":
                if time.time() - int(float(user[0]["lastmsg"])) > 75:
                    if len(message.content) <= 40:
                        await self.bot.primedb.execute(
                            "UPDATE userlevels SET xp = $1 where guildid = $2 AND userid = $3",
                            user[0]["xp"] + 1,
                            guildid,
                            memberid,
                        )
                        print(f"added 1 xp to {message.author}")
                    elif (len(message.content) > 40) and (len(message.content) <= 100):
                        await self.bot.primedb.execute(
                            "UPDATE userlevels SET xp = $1 where guildid = $2 AND userid = $3",
                            user[0]["xp"] + 2,
                            guildid,
                            memberid,
                        )
                        print(f"added 2 xp to {message.author}")
                    elif (len(message.content) > 100) and (len(message.content) <= 250):
                        await self.bot.primedb.execute(
                            "UPDATE userlevels SET xp = $1 where guildid = $2 AND userid = $3",
                            user[0]["xp"] + 3,
                            guildid,
                            memberid,
                        )
                        print(f"added 1 xp to {message.author}")
                    elif len(message.content) > 250:
                        await self.bot.primedb.execute(
                            "UPDATE userlevels SET xp = $1 where guildid = $2 AND userid = $3",
                            user[0]["xp"] + 4,
                            guildid,
                            memberid,
                        )
                        print(f"added 1 xp to {message.author}")

                    await self.bot.primedb.execute(
                        "update userlevels set lastmsg = $1 where guildid = $2 AND userid = $3",
                        time.time(),
                        guildid,
                        memberid,
                    )
                    print(f"set new time for {message.author}")
            botchannel = self.bot.get_channel(804664077891928075)

            member = message.author
            lvl = user[0]["level"]

            roles = {
                6: 798135715728588821,
                10: 751616022364160000,
                12: 798135889314054174,
                18: 798136146991382539,
                32: 798136244139851796,
                50: 798136394081108028,
                69: 798136442718257183,
            }
            # assign roles based on level
            if await self.levelup(user):
                print(f"{member} levelled up")
            if lvl in roles:
                print(f"{member} eligible for rank up role")
                if not roles[lvl] in [x.id for x in member.roles]:
                    role = discord.utils.get(message.guild.roles, id=roles[lvl])
                    await member.add_roles(role)
                    em = discord.Embed(
                        description=f"{member.mention}, you are now {role.mention}. Congratulations.",
                        color=discord.Colour.blue(),
                    )
                    em.set_author(name=f" | Ranked Up ", icon_url=member.avatar_url)

                    print(f"{member} got new role")
                    await botchannel.send(f"{member.mention}")
                    await botchannel.send(embed=em)

    @commands.command(aliases=["rank"])
    async def levelrank(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        data = await self.bot.primedb.fetchrow(
            "select * from userlevels where guildid = $1 and userid = $2",
            ctx.guild.id,
            member.id,
        )

        rawrank = await self.bot.primedb.fetchrow(
            "select rank from(select userlevels.*, rank() over (order by xp desc) as rank from userlevels) userlevels where userid = $1",
            member.id,
        )
        rank = rawrank[0]
        print(rank)

        maxlevelxp = round((6 * ((data["level"]) ** 3)) / 5)
        underlevelxp = round((6 * ((data["level"] - 1) ** 3)) / 5)
        diffxp = round((maxlevelxp - underlevelxp))
        userlevelxp = data["xp"] - underlevelxp
        remainingxp = (diffxp - userlevelxp) + 1

        # await ctx.send(f"{maxlevelxp,underlevelxp,remainingxp,userlevelxp}")

        OldRange = diffxp - 1
        NewXP = round((((userlevelxp - 1) * 99) / OldRange) + 1)
        percent = round((NewXP / 100) * 100)
        print(NewXP)

        pbar = bar(NewXP)

        embed = discord.Embed(colour=discord.Colour.gold())
        embed.set_author(name=f"| Stats for {member.name}", icon_url=member.avatar_url)
        embed.add_field(name="Level", value=f"```{data['level']}```")

        embed.add_field(name="Exp", value=f"```{userlevelxp}```", inline=True)
        embed.add_field(name="Remaining XP", value=f"```{remainingxp}```", inline=True)
        embed.add_field(
            name="Rank", value=f"```{rank}/{ctx.guild.member_count}```", inline=False
        )
        embed.add_field(name="Progress", value=f"```{percent}% {pbar}```", inline=True)

        await ctx.send(embed=embed)

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx, user: discord.Member = None):
        if user is None:
            data = await self.bot.primedb.fetch(
                "select * from userlevels order by xp desc limit 11"
            )

            print(f"{data[0]['userid']} {data[0]['level']} {data[0]}")

            lbtable = PrettyTable(["Rank", "User", "Level", "XP"])

            for i in range(0, 10):
                member = self.bot.get_user(data[i]["userid"])
                if member == ctx.author:
                    username = (
                        member.display_name.encode("ascii", "ignore")
                        .decode("ascii")
                        .capitalize()
                    )
                else:
                    username = (
                        member.display_name.encode("ascii", "ignore")
                        .decode("ascii")
                        .lower()
                    )
                lbtable.add_row(
                    [f"{i+1}", f"{username}", f"{data[i]['level']}", f"{data[i]['xp']}"]
                )

            mlbtable = f"""
            ```ml
{lbtable}```
            """
            em = discord.Embed(description=mlbtable, color=discord.Color.blurple())
            em.set_author(
                name="|     Leaderboard     |  XP", icon_url=ctx.author.avatar_url
            )
            await ctx.send(embed=em)

        else:
            data = await self.bot.primedb.fetchrow(
                f"""select rank,xp from(select userlevels.*, rank() over (order by xp desc) as rank from userlevels) userlevels where userid = $1""",
                user.id,
            )

            underusers = await self.bot.primedb.fetch(
                f"select * from userlevels where xp <= $1 order by xp desc LIMIT $2",
                data[1],
                5,
            )
            topusers = await self.bot.primedb.fetch(
                f"select * from userlevels where xp > $1 order by xp asc LIMIT $2",
                data[1],
                5,
            )

            lbtable = PrettyTable(["Rank", "User", "Level", "XP"])

            for rnk, i in enumerate(reversed(topusers), start=1):
                member = self.bot.get_user(i["userid"])
                if member == ctx.author:
                    username = (
                        member.display_name.encode("ascii", "ignore")
                        .decode("ascii")
                        .capitalize()
                    )
                else:
                    username = (
                        member.display_name.encode("ascii", "ignore")
                        .decode("ascii")
                        .lower()
                    )
                lbtable.add_row(
                    [
                        f"{(data[0] - (6- rnk)) if data[0]>5 else rnk}",
                        f"{username}",
                        f"{i['level']}",
                        f"{i['xp']}",
                    ]
                )
                # lastrank = rnk

            for rnk, i in enumerate((underusers), start=0):
                member = self.bot.get_user(i["userid"])
                if member == user:
                    username = (
                        member.display_name.encode("ascii", "ignore")
                        .decode("ascii")
                        .capitalize()
                    )
                else:
                    username = (
                        member.display_name.encode("ascii", "ignore")
                        .decode("ascii")
                        .lower()
                    )
                lbtable.add_row(
                    [f"{data[0]+rnk}", f"{username}", f"{i['level']}", f"{i['xp']}"]
                )

            mlbtable = f"""
            ```ml
{lbtable}```
            """

            em = discord.Embed(
                title="Leaderboard | XP",
                description=mlbtable,
                color=discord.Color.blurple(),
            )
            em.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=em)


def bar(n: str):
    n = str(n)
    if not n.isdigit():
        return "Invalid value"
    n = int(n)
    if (n < 0) or (n > 100):
        return "Invalid value"
    bar = list("|" + ("░" * 20) + "|")
    num = int(n) // 5
    for x in range(1, num + 1):
        bar[x] = "▓"
    return f"{''.join(bar)}"


def setup(bot):
    bot.add_cog(levelling(bot))
