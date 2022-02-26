import discord
from discord import user
from discord import channel
from discord import client
from discord.errors import Forbidden
from discord.ext import commands
from discord.ext.commands import bot
from discord.utils import get


class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("welcome plugged in.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        homechannel = self.bot.get_channel(751616057567084614)

        await homechannel.send(
            f"""Welcome home, {member.mention}. This server is a creative writing and sci-fi based roleplaying community based upon the planet known as Primordia. To start, simply head to the <#800656996222500865> channel followed by the <#798126442322984961>."""
        )

        try:
            await member.send(
                f"""Welcome home, {member.mention}. This server is a creative writing and sci-fi based roleplaying community based upon the planet known as Primordia. To start, simply head to the #welcome-home channel followed by the #server-guide."""
            )

        except Forbidden:
            pass

        await member.add_roles(member.guild.get_role(751616025623003167))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        auditchannel = self.bot.get_channel(837946269149691986)
        await auditchannel.send(f"{member.mention} has left the server.")


def setup(bot):
    bot.add_cog(welcome(bot))
