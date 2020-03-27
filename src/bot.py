import os
import dice
import re

import aiohttp
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
    print(f'Logged in as {bot.user.name}')

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

VALID_OPERATORS = '+-'
MAX_MESSAGE_LEN = 2000

@bot.command(name='r')
async def roll_dice(ctx, *, arg):
    try:
        arg = arg.replace(' ', '') # Trim whitespace
    
        # collect operators
        operators = ''
        for c in arg:
            if c in VALID_OPERATORS:
                operators += c
        
        elements = re.split('\+|\-', arg) # collect operands

        evaluated_elements = []
        for element in elements:
            if element.isnumeric():
                evaluated_elements.append([int(element)])
            elif re.match('^\d*d?\d+$', element):
                result = [int(i) for i in dice.roll(element)]
                evaluated_elements.append(result)
            else:
                await ctx.send('`Malformed input`')
                return
        
        total = 0
        for i, element in enumerate(evaluated_elements):
            if i == 0 or operators[i-1] == '+':
                total += sum(element)
            elif operators[i-1] == '-':
                total -= sum(element)
        
        if len(evaluated_elements[0]) > 100:
            out_str = '[...]'
        else:
            out_str = str(evaluated_elements[0])

        for i, element in enumerate(evaluated_elements[1:]):
            out_str += ' ' + operators[i]
            if len(element) > 100:
                out_str += ' [...]'
            else:
                out_str += ' ' + str(element)

        out_str = f'{out_str} Total: {total}'
        # messages = [out_str[x:x+MAX_MESSAGE_LEN-2] for x in range(0, len(out_str), MAX_MESSAGE_LEN-2)]
        # for message in messages:
        #     await ctx.send(f'`{message}`')
        await ctx.send(f'`{out_str}`')
    except dice.DiceBaseException as e:
        await ctx.send(f'Error: {e}')

INSPIRO_REQUEST_URL = 'http://inspirobot.me/api?generate=true'
INSIPRO_FAILURE_BACKUP = 'https://generated.inspirobot.me/a/LVPMd1mJXd.jpg'
INSPIRO_IMAGE_URL_PREFIX = 'https://generated.inspirobot.me/a/'

@bot.command(name='inspire')
async def inspire(ctx):
    image_url = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(INSPIRO_REQUEST_URL) as response:
                image_url = await response.text()
    except Exception as e:
        print(e)
            
    if INSPIRO_IMAGE_URL_PREFIX in image_url:
        await ctx.send(image_url)
    else:
        await ctx.send(f'Unknown error. Don\'t worry, I saved one for times like this! {INSIPRO_FAILURE_BACKUP}')

bot.run(TOKEN)