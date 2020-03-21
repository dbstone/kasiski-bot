import os

import discord
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

@bot.command(name='music_test')
async def music_test(ctx):
    if ctx.voice_client:
        ctx.voice_client.play(discord.FFmpegOpusAudio('downloads/current.webm'))

@music_test.before_invoke
async def ensure_voice(ctx):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send('You are not connectd to a voice channel.')
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()

bot.run(TOKEN)