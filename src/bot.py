import os
import re
import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv
import download_youtube
import dice

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PRAC_SERVER = os.getenv('PRAC_SERVER')

MAX_MESSAGE_LEN = 2000
VALID_ROLL_OPERATORS = '+-'
DOWNLOAD_PATH = 'downloads'
INSPIRO_REQUEST_URL = 'http://inspirobot.me/api?generate=true'
INSIPRO_FAILURE_BACKUP = 'https://generated.inspirobot.me/a/LVPMd1mJXd.jpg'
INSPIRO_IMAGE_URL_PREFIX = 'https://generated.inspirobot.me/a/'

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def server(ctx):
    if ctx.message.channel.name == 'csgo':
        await ctx.send(PRAC_SERVER)

@bot.command()
async def play(ctx, *args):
    if ctx.voice_client:
        if args:
            try:
                await download_youtube.download(args[0], DOWNLOAD_PATH, ctx.guild)
            except Exception as e:
                await ctx.send(f'Error: {e}')
                return
            
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    f'{DOWNLOAD_PATH}/{ctx.guild}.webm',
                    options='-vn'
                )
            )
        
            ctx.voice_client.play(
                # discord.FFmpegOpusAudio(f'{DOWNLOAD_PATH}/{ctx.guild}.webm'), 
                source,
                after=lambda e: ctx.voice_client.stop())
        else:
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
            else:
                await ctx.send('You must provide a Youtube URL')

@play.before_invoke
async def ensure_voice(ctx):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send('You are not connected to a voice channel')
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        if ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

# prevent users from using stop and pause commands 
# unless they are in the same voice channel as the bot
async def can_stop(ctx, is_pause):
    if (not ctx.voice_client or 
        (not ctx.voice_client.is_playing() and 
         (is_pause or 
          not ctx.voice_client.is_paused()))):
        await ctx.send('Not currently playing')
        return False

    if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
        await ctx.send('You must connect to the same voice channel as the bot before using this command')
        return False
    
    return True

@bot.command()
async def pause(ctx):
    if await can_stop(ctx, True):
        ctx.voice_client.pause()

@bot.command()
async def stop(ctx):
    if await can_stop(ctx, False):
        ctx.voice_client.stop()

@bot.command(aliases=['dc'])
async def disconnect(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command(aliases=['r'])
async def roll(ctx, *, arg):
    try:
        arg = arg.replace(' ', '') # Trim whitespace
    
        # collect operators
        operators = ''
        for c in arg:
            if c in VALID_ROLL_OPERATORS:
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
        await ctx.send(f'`{out_str}`')
    except dice.DiceBaseException as e:
        await ctx.send(f'Error: {e}')

@bot.command()
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