from dotenv import load_dotenv
import os
import discord
from discord.ext import commands,tasks
from discord.utils import get
import math
from datetime import date
import asyncpg

#set bot token
load_dotenv('auths.env')
TOKEN = os.getenv('TOKEN')

prefix = ["p!","p! ","P!","P! "]
bot = commands.Bot(command_prefix=prefix,case_insensitive=True,intents=discord.Intents.all())
bot.remove_command('help')

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')


@bot.event
async def on_ready():
    game = discord.Game("with ressurection, baby!")
    await bot.change_presence(activity=game)

    print(f"Connected to client {bot.user}") 



@bot.command()
async def ping(ctx):
    async with ctx.typing():
        await ctx.send(f"The latency is {math.ceil(bot.latency * 100)}ms")






for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')




async def create_db_pool():
    bot.primedb = await asyncpg.create_pool(host='135.181.44.255', user='primeuser', password="Fantomex11", database='PrimeDB',port = '5432')
    print("Connected to postgresql server")

 
@tasks.loop(hours=24)
async def called_once_a_day():
    await bot.wait_until_ready()
    await bot.primedb.execute("create table if not exists weatherevents (weather text, description text, url text)")
    message_channel = bot.get_channel(831049193924984882)
    if date.today().weekday() == 0:
        print("today is monday")       
        print(f"Got channel {message_channel}")
        report = await bot.primedb.fetch("SELECT * FROM weatherevents ORDER BY RANDOM() LIMIT 1")
        em=discord.Embed(title = "Weather Report",color = discord.Color.purple(),description = f"```{report[0]['description']}```")
        em.set_image(url = report[0]['url'])
        await message_channel.send(embed=em)

    else:
        print("No Weather Report today")
 
@called_once_a_day.before_loop
async def before():
    await bot.wait_until_ready()
    print("Sending Weather Report")



called_once_a_day.start()


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return
            
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f"The command you specified was not found. Type p!help to see all available commands.")

   
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You are missing a required argument.")

    elif isinstance(error, commands.errors.MissingPermissions) or isinstance(error, discord.Forbidden):
        await ctx.send("You don't have the required permissions for that command. Contact Staff if you think that is a mistake.")

    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(f"You need to wait {error.retry_after:,.2f} seconds before trying this command again.")

    else: await ctx.send(error) 


    
bot.loop.run_until_complete(create_db_pool())
bot.run(TOKEN)
