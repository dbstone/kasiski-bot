import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import download_youtube

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PRAC_SERVER = os.getenv('PRAC_SERVER')

DOWNLOAD_PATH = 'downloads'

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
        ctx.voice_client.play(discord.FFmpegOpusAudio('downloads/music_test.webm'))

@bot.command(name='play_youtube')
async def play_youtube(ctx, url):
    if ctx.voice_client:
        # download song
        download_youtube.download(url, DOWNLOAD_PATH, ctx.guild)
        ctx.voice_client.play(discord.FFmpegOpusAudio(f'{DOWNLOAD_PATH}/{ctx.guild}.webm'))

@play_youtube.before_invoke
@music_test.before_invoke
async def ensure_voice(ctx):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send('You are not connectd to a voice channel.')
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        if ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

bot.run(TOKEN)