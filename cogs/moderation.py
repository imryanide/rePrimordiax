import discord
import discord 
import json
import random 
import datetime
from discord import user
from discord import channel
from discord import client
from discord.ext import commands
from discord.ext.commands import bot
from discord.utils import get
import asyncio


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot=bot

    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation plugged in.")
        await self.bot.primedb.execute("create table if not exists userstrikes (caseid serial primary key, guildid bigint, userid bigint, reason varchar(255), dateissued timestamp, modresp bigint)")
        print("mod table plugged")

    async def sendtoauditlog(self, command, user:discord.Member, channel:discord.TextChannel, victim:discord.Member,reason:str):
        Actionactions= ["Track","Strike","Kick","Ban","Mute","Unmute","Dump", "XP Remove", "XP Add", "Ferin Remove","Ferin Add"]
        dateissued = str(datetime.datetime.now())
        if command in Actionactions:   
            em = discord.Embed(title="Mod Action",description = f"{command} used by {user} in {channel} with reason {reason}",colour=discord.Colour.dark_gold())
            if command == "Track":
                em.title = "Tracked User"
                em.description = f"User was tracked in {channel}"
                em.add_field(name ="Action",value= f"{user} tracked {victim}.")
                em.set_thumbnail(url=victim.avatar_url)
                em.set_author(name=f"{user} used Track", icon_url=user.avatar_url)
                em.set_footer(text=f"Issued on {dateissued}")

            if command == "Strike":
                em.title = "Striked User"
                em.description = f"User was striked in {channel}" 
                em.add_field(name ="Action",value= f"{user} gave a strike to {victim}.")
                em.add_field(name ="Action",value= f" Reason : {reason}")
                em.set_thumbnail(url=victim.avatar_url)
                em.set_author(name=f"{user} gave a strike", icon_url=user.avatar_url)
                em.set_footer(text=f"Issued on {dateissued}")

            if command == "Kick":
                em.title = "Kick"
                em.description = f"User was kicked in {channel}"
                em.add_field(name ="Action",value= f"{user} kicked {victim}.")
                em.add_field(name ="Action",value= f" Reason : {reason}")
                em.set_thumbnail(url=victim.avatar_url)
                em.set_author(name=f"{user} kicked a user", icon_url=user.avatar_url)
                em.set_footer(text=f"Issued on {dateissued}")

            if command == "Ban":
                em.title = "Banned User"
                em.description = f"User was banned in {channel}"
                em.add_field(name ="Action",value= f"{user} banned {victim}.")
                em.add_field(name ="Action",value= f" Reason : {reason}")
                em.set_thumbnail(url=victim.avatar_url)
                em.set_author(name=f"{user} banned an user", icon_url=user.avatar_url)
                em.set_footer(text=f"Issued on {dateissued}")

            if command == "Unmute":
                em.title = "Unmuted User"
                em.description = f"A User was unmuted in {channel}"
                em.add_field(name ="Action",value= f"{victim} was unmuted automatically.")
                em.add_field(name ="Action",value= f" Reason : {reason}")
                em.set_thumbnail(url=victim.avatar_url)
                em.set_author(name=f"{user} unmuted a user", icon_url=user.avatar_url)
                em.set_footer(text=f"Issued on {dateissued}")

            if command == "Dump":
                em.title = "Dumped User"
                em.description = f"User was dumped in {channel}"
                em.add_field(name ="Action",value= f"{user} dumped {victim}.")
                em.add_field(name ="Reason",value= f" {reason}")
                em.set_thumbnail(url=victim.avatar_url)
                em.set_author(name=f"{user} dumped a user", icon_url=user.avatar_url)
                em.set_footer(text=f"Issued on {dateissued}")

            if command == "Strike":
                em.title = "Striked User"
                em.description = f"User was striked in {channel}" 
                em.add_field(name ="Action",value= f"{user} gave a strike to {victim}.")
                em.add_field(name ="Action",value= f" Reason : {reason}")
                em.set_thumbnail(url=victim.avatar_url)
                em.set_author(name=f"{user} gave a strike", icon_url=user.avatar_url)
                em.set_footer(text=f"Issued on {dateissued}")

            


        auditlogchannel = self.bot.get_channel(837946269149691986)
        await auditlogchannel.send(embed=em)




    @commands.command()
    async def trackuser(self,ctx, user:discord.Member = None):
        
        if user is None:
            await ctx.send(f"{ctx.author.mention}, please mention a valid user to track them.")
        
        em = discord.Embed(colour=discord.Colour.blue(), description = "Track")
        result = await self.bot.primedb.fetchrow("SELECT * FROM userstrikes WHERE guildid = $1 and userid = $2",int(ctx.guild.id),int(user.id))
        

        if result is None :
            em.add_field(name = f"{user.name}'s Record" , value="No Record!")
            await ctx.send(embed=em)

        else:
            data = await self.bot.primedb.fetch('select * from userstrikes where guildid = $1 and userid = $2',int(ctx.guild.id),int(user.id)) 
                
                
            for i in range(0,len(data)):
                em.add_field(name = f"Case Id : {data[i][0]}" , value=f"```Reason :{data[i][3]}``` \n```Time Issued : {data[i][4]}``` \n**Responsible Moderator** : <@{data[i][5]}> ",inline=True)

            await self.sendtoauditlog("Track",ctx.author,ctx.channel,user,"Track.")
            await ctx.send(embed=em)
    
    @commands.command()
    @commands.has_guild_permissions(mute_members = True)
    async def strike(self,ctx,user:discord.Member=None,*,reason:str=None):
        
        em = discord.Embed(title="Striked User",colour=discord.Colour.blue())
        em.description = f"User was striked in {ctx.channel}"
        em.add_field(name ="Action",value= f"{ctx.author.mention} gave a strike to {user}.")
        em.add_field(name ="Action",value= f" Reason : {reason}")
        em.set_thumbnail(url=user.avatar_url)
        em.set_author(name=f"{user} received a strike", icon_url=user.avatar_url)
        em.set_footer(text=f"Issued on {ctx.message.created_at}")

        if user is None:
            await ctx.send(f"{ctx.author.mention}, who are you giving a strike to?")
        else:
            if reason is None:
                await ctx.send(f"{ctx.author.mention}, please specify the reason and strike again.")
            else:
                await self.bot.primedb.execute(f"insert into userstrikes (guildid, userid,reason,dateissued,modresp) values ($1,$2,$3,$4,$5)",ctx.guild.id,int(user.id),reason,ctx.message.created_at,int(ctx.author.id))
                await ctx.send(embed=em)
                await user.send(f"You were given a strike in Primordia by {ctx.author.mention} for the reason : \n ```{reason}``` \n on {ctx.message.created_at}. If you would like to appeal this strike, fill out this form :  https://forms.gle/Z8z53Ec78zqW6BLH8.")
                await self.sendtoauditlog("Strike",ctx.author,ctx.channel,user,reason)

    @commands.command()
    @commands.has_guild_permissions(ban_members = True)
    async def ban(self,ctx,user:discord.Member,*,reason:str=None):
        
        
        em = discord.Embed(title="Banned User",colour=discord.Colour.dark_gold())
        em.description = f"User was banned in {ctx.channel}"
        em.add_field(name ="Action",value= f"{ctx.author.mention} banned {user}")
        em.add_field(name ="Action",value= f" Reason : {reason}")
        em.set_thumbnail(url=user.avatar_url)
        em.set_author(name=f"{user} was banned", icon_url=user.avatar_url)
        em.set_footer(text=f"Issued on {ctx.message.created_at}")

        if user is None:
            await ctx.send(f"{ctx.author.mention}, who are you banning?")
        
        if reason is None:
            await ctx.send(f"{ctx.author.mention}, please specify the reason.")
        else:
            
            await ctx.send(embed = em)
            await self.sendtoauditlog("Ban",ctx.author,ctx.channel,user,reason)
            await user.send(f"You were banned in Primordia by {ctx.author.mention} for the reason : \n ```{reason}``` \n on {ctx.message.created_at}. If you would like to appeal this ban, fill out this form :  https://forms.gle/Z8z53Ec78zqW6BLH8.")
            await user.ban(reason=reason)
    
    @commands.command()
    @commands.has_guild_permissions(kick_members = True)
    async def kick(self,ctx,user:discord.Member,*,reason:str=None):
        
        em = discord.Embed(title="Kicked User")
        em.description = f"User was kicked in {ctx.channel}"
        em.add_field(name ="Action",value= f"{ctx.author.mention} kicked {user}")
        em.add_field(name ="Action",value= f" Reason : {reason}")
        em.set_thumbnail(url=user.avatar_url)
        em.set_author(name=f"{user} was kicked", icon_url=user.avatar_url)
        em.set_footer(text=f"Issued on {ctx.message.created_at}")

        if user is None:
            await ctx.send(f"{ctx.author.mention}, who are you kicking?")
        
        if reason is None:
            await ctx.send(f"{ctx.author.mention}, please specify the reason.")
        else:
            
            await ctx.send(embed=em)
            await self.sendtoauditlog("Kick",ctx.author,ctx.channel,user,reason)
            await user.send(f"You were kicked in Primordia by {ctx.author.mention} for the reason : \n ```{reason}``` \n on {ctx.message.created_at}. If you would like to appeal this, fill out this form :  https://forms.gle/Z8z53Ec78zqW6BLH8.")
            await user.kick(reason=reason)


    @commands.command()
    @commands.has_guild_permissions(mute_members = True)
    async def mute(self,ctx,member:discord.Member,time: int,d, *,reason:str=None):
        
        if member is None:
            await ctx.send(f"{ctx.author.mention}, who are you muting?")     
         
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")
        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")

            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
        
        if reason is None:
            await ctx.send(f"{ctx.author.mention}, please specify the reason.")
        else:
            await member.add_roles(mutedRole)

            embed = discord.Embed(title="User Muted", description=f"{member.mention} has been muted by {ctx.author.mention} ", colour=discord.Colour.green())
            embed.add_field(name="reason:", value=reason, inline=False)
            embed.add_field(name="Duration :", value=f"{time}{d}", inline=False)
            embed.set_author(name = "User muted", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            await self.sendtoauditlog("Mute",ctx.author,ctx.channel,member,reason)
            await member.send(embed=embed)
            await member.send(f"If you would like to appeal this decision, fill out this form : https://forms.gle/Z8z53Ec78zqW6BLH8")


            if d == "s":
                await asyncio.sleep(time)

            if d == "m":
                await asyncio.sleep(time*60)

            if d == "h":
                await asyncio.sleep(time*60*60)

            if d == "d":
                await asyncio.sleep(time*60*60*24)

            await member.remove_roles(mutedRole)

            embed = discord.Embed(title="Unmuted", description=f"Unmuted -{member.mention} ", colour=discord.Colour.light_gray())
            await self.sendtoauditlog("Unmute",ctx.author,ctx.channel,member,reason)
            await ctx.invoke(self.bot.get_command('strike'), user= member, reason= reason)
            await ctx.send(embed=embed)
            await member.send(embed=embed)

    
    @commands.command()
    @commands.has_guild_permissions(mute_members = True)
    async def unmute(self,ctx,member:discord.Member):
        

        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
        
        await member.remove_roles(mutedRole)
        await self.sendtoauditlog("Unmute",ctx.author,ctx.channel,member,"Unmuted")
        embed = discord.Embed(title="unmute (temp) ", description=f"unmuted -{member.mention} ", colour=discord.Colour.light_gray())
        await ctx.send(embed=embed)
        await member.send(embed=embed)

    @commands.command()
    @commands.has_guild_permissions(kick_members = True)
    async def dump(self,ctx,member:discord.Member):        
        dumpRole = discord.utils.get(ctx.guild.roles, name="Dumped")
        
        await member.add_roles(dumpRole)
        await self.sendtoauditlog("Dump",ctx.author,ctx.channel,member,"Dumped")
        emb = discord.Embed(description=f"{member.mention} has been banished.", colour=discord.Colour.red())
        emb.set_author(name = "Dumped",icon_url=member.avatar_url)
        await ctx.send(embed=emb)
        await member.send(embed=emb)

    @commands.command()
    @commands.has_guild_permissions(kick_members = True)
    async def removexp(self,ctx,member:discord.Member=None, amount:int=0):
        if member is None:
            await ctx.send(f"{ctx.author.mention}, who are you removing xp from?")


        await self.bot.primedb.execute("update userlevels set xp = xp - $1 where guildid = $2 AND userid = $3",amount,ctx.guild.id,member.id)
        await ctx.send(f"{amount} xp has been removed from {member.mention}.")
        await self.sendtoauditlog("XP Remove", ctx.author,ctx.channel,member,"XP Removed")

    @commands.command()
    @commands.has_guild_permissions(kick_members = True)
    async def addxp(self,ctx,member:discord.Member=None, amount:int=0):
        if member is None:
            await ctx.send(f"{ctx.author.mention}, who are you adding xp to?")

        await self.bot.primedb.execute("update userlevels set xp = xp + $1 where guildid = $2 AND userid = $3",amount,ctx.guild.id,member.id)
        await ctx.send(f"{amount} xp has been added to {member.mention}.")
        await self.sendtoauditlog("XP Add", ctx.author,ctx.channel,member,"XP Added")

    @commands.command()
    @commands.has_guild_permissions(kick_members = True)
    async def removeferins(self,ctx,member:discord.Member=None, amount:int=0):
        if member is None:
            await ctx.send(f"{ctx.author.mention}, who are you removing ferins from?")
        await self.bot.primedb.execute("update userferins set ferins = ferins - $1 where guildid = $2 AND userid = $3",amount,ctx.guild.id,member.id)
        await ctx.send(f"{amount} ferins have been removed from {member.mention}.")
        await self.sendtoauditlog("Ferin Remove", ctx.author,ctx.channel,member,"Ferin Removed")

    @commands.command()
    @commands.has_guild_permissions(kick_members = True)
    async def addferins(self,ctx,member:discord.Member=None, amount:int=0):
        if member is None:
            await ctx.send(f"{ctx.author.mention}, who are you removing ferins from?")

        await self.bot.primedb.execute("update userferins set ferins = ferins + $1 where guildid = $2 AND userid = $3",amount,ctx.guild.id,member.id)
        await ctx.send(f"{amount} ferins have been added to {member.mention}.")
        await self.sendtoauditlog("Ferin Add", ctx.author,ctx.channel,member,"Ferin Added")


            


def setup(bot):
    bot.add_cog(Moderation(bot))