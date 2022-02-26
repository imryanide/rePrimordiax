from ntpath import join
import discord
from discord import message
from discord.errors import NoMoreItems
from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageOps
from io import BytesIO
import datetime
from discord.ext.commands import bot
from prettytable import PrettyTable
from prettytable.prettytable import PLAIN_COLUMNS

bannershop = {
    "darkroses": [5000, "white"],  # base price,font color to use
    "daymountains": [4500, "black"],
    "fibers": [4500, "white"],
    "lava": [5000, "white"],
    "lightning": [4500, "white"],
    "matrix": [6000, "white"],
    "mountain": [5500, "white"],
    "palmleaves": [6000, "white"],
    "skyrise": [5500, "black"],
    "custom": [17500, "white"],
    "wormhole": [100, "white"],
}


class userstats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("userstats plugged in.")
        await self.bot.primedb.execute(
            "create table if not exists userlevels (guildid bigint, userid bigint, level bigint,xp bigint, lastmsg real, unique(userid, guildid))"
        )
        await self.bot.primedb.execute(
            "create table if not exists userferins (guildid bigint, userid bigint, ferins bigint, lastmsg real, unique(userid, guildid))"
        )
        await self.bot.primedb.execute(
            "create table if not exists userdetails (guildid bigint, userid bigint, activebackground text, backgrounds text[] , featuredchar text, unique(userid, guildid))"
        )

    @commands.command()
    async def checkinv(self, ctx):
        if ctx.author.id == 746384558831698012:
            # await self.bot.primedb.execute("UPDATE userdetails SET backgrounds = array_append(backgrounds,$1) WHERE userid = $2 AND guildid = $3",banner,ctx.author.id,ctx.guild.id)
            user = await self.bot.primedb.fetch(
                "SELECT * FROM userdetails WHERE userid = $1 AND guildid = $2",
                ctx.author.id,
                ctx.guild.id,
            )
            await ctx.send(f"{user[0]['backgrounds']} \n {user[0]['backgrounds'][1]}")

    @commands.command()
    async def addinv(self, ctx, banner):
        if ctx.author.id == 746384558831698012:
            await self.bot.primedb.execute(
                "UPDATE userdetails SET backgrounds = array_append(backgrounds,$1) WHERE userid = $2 AND guildid = $3",
                banner,
                ctx.author.id,
                ctx.guild.id,
            )
            user = await self.bot.primedb.fetch(
                "SELECT * FROM userdetails WHERE userid = $1 AND guildid = $2",
                ctx.author.id,
                ctx.guild.id,
            )
            await ctx.send(
                f"{banner} added to inv \n {user} \n {user[0]['backgrounds']} \n {user[0]['backgrounds'][1]}"
            )

    @commands.command()
    async def buybanner(self, ctx, banner: str = None):
        user = await self.bot.primedb.fetch(
            "SELECT * FROM userdetails WHERE userid = $1 AND guildid = $2",
            ctx.author.id,
            ctx.guild.id,
        )
        if not user:
            user = await self.bot.primedb.fetch(
                "INSERT INTO userdetails (userid, guildid, activebackground, backgrounds, featuredchar) VALUES ($1, $2, $3, $4, $5) RETURNING *",
                ctx.author.id,
                ctx.guild.id,
                "wormhole",
                {"wormhole"},
                "unset",
            )
        if banner in list(bannershop.keys()) and banner not in user[0]["backgrounds"]:
            ferindata = await self.bot.primedb.fetch(
                "SELECT * FROM userferins WHERE userid = $1 AND guildid = $2",
                ctx.author.id,
                ctx.guild.id,
            )
            price = bannershop[banner][0]
            ownedno = len(user[0]["backgrounds"])
            price = price + (250 * ownedno)
            print(price)
            if price < ferindata[0]["ferins"]:
                m = await ctx.send(
                    f"This banner costs `{price}` ferins. Are you sure you want to buy it?",
                    components=[Button(style=ButtonStyle.green, label="Yes")],
                )

                def check(res):
                    return ctx.author == res.user and res.channel == ctx.channel

                try:
                    res = await self.bot.wait_for(
                        "button_click", check=check, timeout=15
                    )
                    await res.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        content=f"{res.component.label} chosen.",
                    )
                    await self.bot.primedb.execute(
                        "UPDATE userdetails SET backgrounds = array_append(backgrounds,$1) WHERE userid = $2 AND guildid = $3",
                        banner,
                        ctx.author.id,
                        ctx.guild.id,
                    )
                    await self.bot.primedb.execute(
                        "UPDATE userferins SET ferins = ferins - $1 WHERE guildid = $2 AND userid = $3",
                        price,
                        ctx.guild.id,
                        ctx.author.id,
                    )
                    if banner == "custom":
                        await ctx.send(
                            f"Congrats, you bought a custom banner! Dm <@746384558831698012> with your image."
                        )
                    else:
                        em = discord.Embed(
                            description=f"You have bought the banner `{banner}` at {price} ferins.\nYou can now equip this banner with `p!setprofile banner {banner}`. \n Remaining Ferins : {ferindata[0]['ferins']}",
                            color=discord.Color.green(),
                        )
                        em.set_author(
                            name=f"{ctx.author.display_name} > Banner Bought",
                            icon_url=ctx.author.avatar_url,
                        )
                        em.set_footer(
                            text="Please note prices of banner go up depending on how many banners you have."
                        )
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

            else:
                await ctx.send(
                    f"{ctx.author.mention}, this banner costs `{price}` ferins. You do not have enough ferin to purchase this."
                )
        else:
            invalidbanner = f"You have entered a non existent banner! The current banners available are : \n```darkroses , daymountains , fibers , lava , lightning , matrix , mountain , palmleaves , skyrise , wormhole``` \nIf you want a custom image, you can buy one with `p!buybanner custom`"
            ownedbanner = f"You already have this item in your inventory!"
            em = discord.Embed(
                description=ownedbanner
                if banner in user[0]["backgrounds"]
                else invalidbanner,
                color=discord.Color.red(),
            )
            await ctx.send(embed=em)

    @commands.command()
    async def setprofile(self, ctx, ptype: str = None, *, character: str = None):
        if ptype is None or character is None:
            await ctx.send(
                f"{ctx.author.mention}, you have not set your profile details. Please retry the command."
            )
        else:
            user = await self.bot.primedb.fetch(
                "SELECT * FROM userdetails WHERE userid = $1 AND guildid = $2",
                ctx.author.id,
                ctx.guild.id,
            )
            if not user:
                user = await self.bot.primedb.fetch(
                    "INSERT INTO userdetails (userid, guildid, activebackground, backgrounds, featuredchar) VALUES ($1, $2, $3, $4, $5) RETURNING *",
                    ctx.author.id,
                    ctx.guild.id,
                    "wormhole",
                    {"wormhole"},
                    "unset",
                )

            if ptype == "banner":
                if character not in user[0]["backgrounds"]:
                    await ctx.send(
                        f"{ctx.author.mention}, you do not have that banner in your inventory. Consider buying it using `p!buybanner {character}` if you have enough ferins."
                    )
                else:
                    await self.bot.primedb.execute(
                        "UPDATE userdetails SET activebackground = $1 WHERE userid = $2 AND guildid = $3",
                        character,
                        ctx.author.id,
                        ctx.guild.id,
                    )
                    await ctx.send(
                        f"{ctx.author.mention}, your banner is now set to `{character}`."
                    )

            elif ptype == "char" or ptype == "character":
                await self.bot.primedb.execute(
                    "UPDATE userdetails SET featuredchar = $1 WHERE userid = $2 AND guildid = $3",
                    character,
                    ctx.author.id,
                    ctx.guild.id,
                )
                await ctx.send(
                    f"{ctx.author.mention}, your character is now set to `{character}`."
                )

            else:
                await ctx.send(
                    f"{ctx.author.mention}, you have not chosen a valid profile field to update. Your options are \n`banner` \n`character`"
                )

            user = await self.bot.primedb.fetch(
                "SELECT * FROM userdetails WHERE userid = $1 AND guildid = $2",
                ctx.author.id,
                ctx.guild.id,
            )

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def profile(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        userdata = await self.bot.primedb.fetch(
            "SELECT * FROM userdetails WHERE userid = $1 AND guildid = $2",
            user.id,
            ctx.guild.id,
        )
        if not userdata:
            userdata = await self.bot.primedb.fetch(
                "INSERT INTO userdetails (userid, guildid, activebackground, backgrounds, featuredchar) VALUES ($1, $2, $3, $4, $5) RETURNING *",
                user.id,
                ctx.guild.id,
                "wormhole",
                {"wormhole"},
                "unset",
            )

        # get user data
        leveldata = await self.bot.primedb.fetchrow(
            "select * from userlevels where guildid = $1 and userid = $2",
            ctx.guild.id,
            user.id,
        )
        ferindata = await self.bot.primedb.fetchrow(
            "SELECT * FROM userferins WHERE userid = $1 AND guildid = $2",
            user.id,
            ctx.guild.id,
        )
        ferins = ferindata["ferins"]
        level = leveldata["level"]
        levelrank = await self.bot.primedb.fetchrow(
            "select rank from(select userlevels.*, rank() over (order by xp desc) as rank from userlevels) userlevels where userid = $1",
            user.id,
        )
        ferinrank = await self.bot.primedb.fetchrow(
            "select rank from(select userferins.*, rank() over (order by ferins desc) as rank from userferins) userferins where userid = $1",
            ctx.author.id,
        )

        roles = {
            6: 798135715728588821,
            10: 751616022364160000,
            12: 798135889314054174,
            18: 798136146991382539,
            32: 798136244139851796,
            50: 798136394081108028,
            69: 798136442718257183,
        }
        if userroles := [
            role.name for role in user.roles if role.id in (roles.values())
        ]:
            toprole = userroles[-1]
        else:
            toprole = "Unranked"
        userjoindate = user.joined_at.strftime("%b %d %Y")

        featuredchar = userdata[0]["featuredchar"]
        banner = userdata[0]["activebackground"]
        fontcolor = bannershop[banner][1]

        ###############################################################################################################################################################################################

        # Import Fonts
        if len(str(user)) >= 14:
            bigfont = ImageFont.truetype("data/centurygothic.ttf", 56)
        else:
            bigfont = ImageFont.truetype("data/centurygothic.ttf", 60)
        smallfont = ImageFont.truetype("data/centurygothic.ttf", 36)

        if ferins > 9 or level > 9:
            numfont = ImageFont.truetype("data/centurygothic.ttf", 56)
        else:
            numfont = ImageFont.truetype("data/centurygothic.ttf", 62)
        # Open Image and get user avatar
        profilebg = Image.open(f"data/{banner}.png")
        useravatar = user.avatar_url_as(size=128)
        usavdata = BytesIO(await useravatar.read())
        pfp = Image.open(usavdata)

        # Draw object
        draw = ImageDraw.Draw(profilebg)

        # Type out text

        if fontcolor == "white":
            draw.text(
                (240, 65), f"{user}", (255, 255, 255), font=bigfont
            )  # draw username
            draw.text(
                (240, 150), toprole, (255, 255, 255), font=smallfont
            )  # draw top rank role
            draw.text(
                (240, 190), featuredchar, (255, 255, 255), font=smallfont
            )  # draw featured character
            draw.text(
                (240, 230), f"Ferins", (255, 255, 255), font=smallfont
            )  # draw ferins
            draw.text(
                (240, 270), f"Level", (255, 255, 255), font=smallfont
            )  # draw levels
            draw.text(
                (240, 310), f"Joined", (255, 255, 255), font=smallfont
            )  # draw join date

            draw.text((370, 230), f"|", (255, 255, 255), font=smallfont)
            draw.text((370, 270), f"|", (255, 255, 255), font=smallfont)
            draw.text((370, 310), f"|", (255, 255, 255), font=smallfont)

            draw.text((400, 230), f"{ferins}", (255, 255, 255), font=smallfont)
            draw.text((400, 270), f"{level}", (255, 255, 255), font=smallfont)
            draw.text((400, 310), f"{userjoindate}", (255, 255, 255), font=smallfont)

            if ferinrank[0] <= 9:
                draw.text(
                    (51, 270), f"{ferinrank[0]}", (255, 255, 255), font=numfont
                )  # draw ferin rank
            else:
                draw.text(
                    (47, 270), f"{ferinrank[0]}", (255, 255, 255), font=numfont
                )  # draw ferin rank

            if levelrank[0] <= 9:
                draw.text(
                    (145, 270), f"{levelrank[0]}", (255, 255, 255), font=numfont
                )  # draw leaderboard rank
            else:
                draw.text(
                    (140, 270), f"{levelrank[0]}", (255, 255, 255), font=numfont
                )  # draw leaderboard rank

        elif fontcolor == "black":
            draw.text((240, 65), f"{user}", (0, 0, 0), font=bigfont)  # draw username
            draw.text(
                (240, 150), toprole, (0, 0, 0), font=smallfont
            )  # draw top rank role
            draw.text(
                (240, 190), featuredchar, (0, 0, 0), font=smallfont
            )  # draw featured character
            draw.text((240, 230), f"Ferins", (0, 0, 0), font=smallfont)  # draw ferins
            draw.text((240, 270), f"Level", (0, 0, 0), font=smallfont)  # draw levels
            draw.text(
                (240, 310), f"Joined", (0, 0, 0), font=smallfont
            )  # draw join date

            draw.text((370, 230), f"|", (0, 0, 0), font=smallfont)
            draw.text((370, 270), f"|", (0, 0, 0), font=smallfont)
            draw.text((370, 310), f"|", (0, 0, 0), font=smallfont)

            draw.text((400, 230), f"{ferins}", (0, 0, 0), font=smallfont)
            draw.text((400, 270), f"{level}", (0, 0, 0), font=smallfont)
            draw.text((400, 310), f"{userjoindate}", (0, 0, 0), font=smallfont)

            if ferinrank[0] <= 9:
                draw.text(
                    (52, 270), f"{ferinrank[0]}", (255, 255, 255), font=numfont
                )  # draw ferin rank
            else:
                draw.text(
                    (47, 270), f"{ferinrank[0]}", (255, 255, 255), font=numfont
                )  # draw ferin rank

            if levelrank[0] < 10:
                draw.text(
                    (145, 270), f"{levelrank[0]}", (255, 255, 255), font=numfont
                )  # draw leaderboard rank
            else:
                draw.text(
                    (142, 270), f"{levelrank[0]}", (255, 255, 255), font=numfont
                )  # draw leaderboard rank

        # (50,45),128 - pfp coords
        # (250,45) - username coords
        # (250,110) - other text coords

        # put a mask over pfp ##################################################################################################

        bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
        print(bigsize)
        mask = Image.new("L", bigsize, 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(pfp.size, Image.ANTIALIAS)
        print(pfp.size)
        maskedpfp = ImageOps.fit(pfp, mask.size, centering=(0.5, 0.5))
        maskedpfp.putalpha(mask)

        ########################################################################################################################

        profilebg.paste(maskedpfp, (52, 62), mask=mask)
        profilebg.save("profile.png")
        file = discord.File("profile.png")
        em = discord.Embed(color=discord.Color.dark_teal())
        em.set_author(name="Profile", icon_url=user.avatar_url)
        em.set_image(url="attachment://profile.png")
        await ctx.send(file=file, embed=em)

    @profile.error
    async def profile_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = str(datetime.timedelta(seconds=int(error.retry_after)))
            em = discord.Embed(
                description=f"{ctx.author.mention}, you are on cooldown! You can use this command in `{remaining_time}` ",
                color=discord.Color.red(),
            )
            em.set_author(name="Cooldown!", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(userstats(bot))
