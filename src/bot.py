import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PRAC_SERVER = os.getenv('PRAC_SERVER')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

@bot.command(name='echo')
async def echo(ctx, *, arg):
    await ctx.send(arg)

@bot.command(name='saymyname')
async def echo(ctx):
    await ctx.send(ctx.message.author)

@bot.command(name='server')
async def server(ctx):
    if ctx.message.channel.name == 'csgo':
        await ctx.send(PRAC_SERVER)

bot.run(TOKEN)