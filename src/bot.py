import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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

bot.run(TOKEN)