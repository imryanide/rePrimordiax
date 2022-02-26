import discord
import random
from discord import message
from discord import colour
from discord.ext import commands
import datetime
import time
from prettytable import PrettyTable


class ferins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ferins plugged in.")
        await self.bot.primedb.execute(
            "create table if not exists userferins (guildid bigint, userid bigint, ferins bigint, lastmsg real, unique(userid, guildid))"
        )
        print("ferins table plugged")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            memberid = message.author.id
            guildid = message.guild.id

            user = await self.bot.primedb.fetch(
                "SELECT * FROM userferins WHERE userid = $1 AND guildid = $2",
                memberid,
                guildid,
            )

            if not user:
                user = await self.bot.primedb.fetch(
                    "INSERT INTO userferins (userid, guildid, ferins, lastmsg) VALUES ($1, $2, $3, $4) RETURNING *",
                    memberid,
                    guildid,
                    1,
                    time.time(),
                )

            # user = await self.bot.primedb.fetchrow("SELECT * FROM userferins WHERE userid = $1 AND guildid = $2", memberid, guildid)

            if time.time() - int(float(user[0]["lastmsg"])) > 360:
                chance = random.randint(1, 100)
                if chance >= 60:
                    if len(message.content) <= 40:
                        await self.bot.primedb.execute(
                            "UPDATE userferins SET ferins = $1 where guildid = $2 AND userid = $3",
                            user[0]["ferins"] + 3,
                            guildid,
                            memberid,
                        )

                    elif (len(message.content) > 40) and (len(message.content) <= 100):
                        await self.bot.primedb.execute(
                            "UPDATE userferins SET ferins = $1 where guildid = $2 AND userid = $3",
                            user[0]["ferins"] + 4,
                            guildid,
                            memberid,
                        )

                    elif (len(message.content) > 100) and (len(message.content) <= 250):
                        await self.bot.primedb.execute(
                            "UPDATE userferins SET ferins = $1 where guildid = $2 AND userid = $3",
                            user[0]["ferins"] + 5,
                            guildid,
                            memberid,
                        )

                    elif len(message.content) > 250:
                        await self.bot.primedb.execute(
                            "UPDATE userferins SET ferins = $1 where guildid = $2 AND userid = $3",
                            user[0]["ferins"] + 8,
                            guildid,
                            memberid,
                        )

                await self.bot.primedb.execute(
                    "update userferins set lastmsg = $1 where guildid = $2 AND userid = $3",
                    time.time(),
                    guildid,
                    memberid,
                )

    @commands.command(aliases=["balance", "bal"])
    async def ferinbalance(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        rawrank = await self.bot.primedb.fetchrow(
            "select rank from(select userferins.*, rank() over (order by ferins desc) as rank from userferins) userferins where userid = $1",
            ctx.author.id,
        )
        rank = rawrank[0]
        print(rank)
        ferinamt = await self.bot.primedb.fetchrow(
            "select ferins from userferins where userid = $1 and guildid = $2",
            ctx.author.id,
            ctx.guild.id,
        )

        embed = discord.Embed(colour=discord.Colour.blurple())
        embed.set_author(name=f"| {member.name}'s Balance", icon_url=member.avatar_url)
        embed.add_field(name="Ferin Balance", value=f"```{ferinamt['ferins']}```")
        embed.add_field(name="Rank", value=f"```{rank}/{ctx.guild.member_count}```")

        await ctx.send(embed=embed)

    @commands.command(aliases=["flb"])
    async def ferinleaderboard(self, ctx):
        data = await self.bot.primedb.fetch(
            "select * from userferins order by ferins desc limit 11"
        )

        print(f"{data[0]['userid']} {data[0]['ferins']} {data[0]}")

        lbtable = PrettyTable(["Rank", "User", "Ferins"])

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
            lbtable.add_row([f"{i+1}", f"{username}", f"{data[i]['ferins']}"])

        mlbtable = f"""
        ```ml
{lbtable}```
        """
        em = discord.Embed(description=mlbtable, color=discord.Color.blurple())
        em.set_author(
            name="|     Leaderboard     |  Ferins", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def work(self, ctx):
        member = ctx.author
        memberid = ctx.author.id
        guildid = ctx.guild.id
        user = await self.bot.primedb.fetch(
            "SELECT * FROM userferins WHERE userid = $1 AND guildid = $2",
            memberid,
            guildid,
        )

        if not user:
            await self.bot.primedb.fetch(
                "INSERT INTO userferins (userid, guildid, ferins, lastmsg) VALUES ($1, $2, $3, $4) RETURNING *",
                memberid,
                guildid,
                1,
                time.time(),
            )

        # user = await self.bot.primedb.fetchrow("SELECT * FROM userferins WHERE userid = $1 AND guildid = $2", memberid, guildid)

        lvlroles = {
            "Rank: Scavenger": (50, 80),
            "Rank: Survivor": (40, 60),
            "Rank: Battleworn": (40, 60),
            "Rank: Warrior": (50, 55),
            "Rank: Sage": (50, 60),
            "Rank: Ascended": (50, 80),
        }

        if roles := [
            role.name for role in member.roles if role.name in list(lvlroles.keys())
        ]:
            asgnd = random.randint((lvlroles[roles[-1]][0]), (lvlroles[roles[-1]][1]))
            await self.bot.primedb.execute(
                "UPDATE userferins SET ferins = $1 where guildid = $2 AND userid = $3",
                user[0]["ferins"] + asgnd,
                guildid,
                memberid,
            )
            print(f"{asgnd} ferins assigned cause of role {roles[0]}")
            emb = discord.Embed(
                description=f"You worked hard, earning some ferins. \n```Ferins Earned : {asgnd}```",
                color=discord.Color.green(),
            )
            emb.set_author(name=f"Earned Ferins | {member}", icon_url=member.avatar_url)
            emb.set_footer(text="You earned extra ferins due to your rank.")
            await ctx.send(embed=emb)

        else:
            await self.bot.primedb.execute(
                "UPDATE userferins SET ferins = $1 where guildid = $2 AND userid = $3",
                user[0]["ferins"] + 5,
                guildid,
                memberid,
            )
            emb = discord.Embed(
                description=f"You worked hard, earning some ferins. \n```Ferins Earned : 5 ```",
                color=discord.Color.green(),
            )
            emb.set_author(name=f"Earned Ferins | {member}", icon_url=member.avatar_url)
            await ctx.send(embed=emb)

    @work.error
    async def work_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = str(datetime.timedelta(seconds=int(error.retry_after)))
            em = discord.Embed(
                description=f"{ctx.author.mention}, you are on cooldown! You can use this command in `{remaining_time}` ",
                color=discord.Color.red(),
            )
            em.set_author(name="Cooldown!", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        member = ctx.author
        memberid = ctx.author.id
        guildid = ctx.guild.id
        user = await self.bot.primedb.fetch(
            "SELECT * FROM userferins WHERE userid = $1 AND guildid = $2",
            memberid,
            guildid,
        )
        if not user:
            await self.bot.primedb.fetch(
                "INSERT INTO userferins (userid, guildid, ferins, lastmsg) VALUES ($1, $2, $3, $4) RETURNING *",
                memberid,
                guildid,
                1,
                time.time(),
            )

        lvlroles = {
            "Rank: Scavenger": (70, 180),
            "Rank: Survivor": (110, 200),
            "Rank: Battleworn": (120, 220),
            "Rank: Warrior": (220, 300),
            "Rank: Sage": (250, 360),
            "Rank: Ascended": (250, 380),
        }

        if roles := [
            role.name for role in member.roles if role.name in list(lvlroles.keys())
        ]:
            asgnd = random.randint((lvlroles[roles[-1]][0]), (lvlroles[roles[-1]][1]))
            await self.bot.primedb.execute(
                "UPDATE userferins SET ferins = $1 where guildid = $2 AND userid = $3",
                user[0]["ferins"] + asgnd,
                guildid,
                memberid,
            )
            print(f"{asgnd} ferins assigned cause of role {roles[0]}")
            emb = discord.Embed(
                description=f"You wake up to a fresh day, redeeming your ferins. \n ```{asgnd} ferins gained!```",
                color=discord.Color.green(),
            )
            emb.set_author(name=f"Earned Ferins | {member}", icon_url=member.avatar_url)
            emb.set_footer(text="You earned extra ferins due to your rank.")
            await ctx.send(embed=emb)

    @daily.error
    async def daily_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = str(datetime.timedelta(seconds=int(error.retry_after)))
            em = discord.Embed(
                description=f"{ctx.author.mention}, you are on cooldown! You can use this command in `{remaining_time}` ",
                color=discord.Color.red(),
            )
            em.set_author(name="Cooldown!", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def gamble(self, ctx, amount: int = None):
        if amount is None:
            await ctx.send(
                f"{ctx.author.mention}, you havent mentioned how much you want to gamble!"
            )
            ctx.command.reset_cooldown(ctx)
        member = ctx.author
        memberid = ctx.author.id
        guildid = ctx.guild.id
        ferindata = await self.bot.primedb.fetch(
            "SELECT * FROM userferins WHERE userid = $1 AND guildid = $2",
            memberid,
            guildid,
        )
        if not ferindata:
            await self.bot.primedb.fetch(
                "INSERT INTO userferins (userid, guildid, ferins, lastmsg) VALUES ($1, $2, $3, $4) RETURNING *",
                memberid,
                guildid,
                1,
                time.time(),
            )

        if amount < ferindata[0]["ferins"]:

            m = await ctx.send(
                f"Do you want to gamble {amount} ferins?",
                components=[Button(style=ButtonStyle.green, label="Yes")],
                delete_after=30,
            )

            def check(res):
                return ctx.author == res.user and res.channel == ctx.channel

            try:
                res = await self.bot.wait_for("button_click", check=check, timeout=15)
                await res.respond(
                    type=InteractionType.ChannelMessageWithSource,
                    content=f"{res.component.label} chosen.",
                )
                success = random.randint(1, 100)
                if success >= 60:
                    await m.delete()
                    await self.bot.primedb.execute(
                        "UPDATE userferins SET ferins = ferins + $1 WHERE guildid = $2 AND userid = $3",
                        amount,
                        ctx.guild.id,
                        ctx.author.id,
                    )
                    em = discord.Embed(
                        description=f"You have won the gamble! \n{amount} ferins have been added to your account.",
                        color=discord.Color.green(),
                    )
                    em.set_author(name="Success", icon_url=member.avatar_url)
                    await ctx.send(embed=em)
                else:
                    await m.delete()
                    await self.bot.primedb.execute(
                        "UPDATE userferins SET ferins = ferins - $1 WHERE guildid = $2 AND userid = $3",
                        amount,
                        ctx.guild.id,
                        ctx.author.id,
                    )
                    em = discord.Embed(
                        description=f"You have lost the gamble :( \n{amount} ferins have been subtracted from your account.",
                        color=discord.Color.red(),
                    )
                    em.set_author(name="Loss", icon_url=member.avatar_url)
                    await ctx.send(embed=em)

            except TimeoutError:
                await m.edit(
                    "Timed out!",
                    components=[
                        Button(
                            style=ButtonStyle.red, label="Timed out!", disabled=True
                        ),
                    ],
                )

    @gamble.error
    async def gamble_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = str(datetime.timedelta(seconds=int(error.retry_after)))
            em = discord.Embed(
                description=f"{ctx.author.mention}, you are on cooldown! You can use this command in `{remaining_time}`",
                color=discord.Color.red(),
            )
            em.set_author(name="Cooldown!", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(ferins(bot))
