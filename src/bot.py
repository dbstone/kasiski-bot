# built-in
import os

# third-party
from discord.ext import commands
from dotenv import load_dotenv

# local
import roll
import audio

# init constants stored in .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PRAC_SERVER = os.getenv('PRAC_SERVER')

INSPIRO_REQUEST_URL = 'http://inspirobot.me/api?generate=true'
INSIPRO_FAILURE_BACKUP = 'https://generated.inspirobot.me/a/LVPMd1mJXd.jpg'
INSPIRO_IMAGE_URL_PREFIX = 'https://generated.inspirobot.me/a/'

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(aliases=['prac'], hidden=True)
async def server(ctx):
    if ctx.message.channel.name == 'csgo':
        await ctx.send(PRAC_SERVER)

@bot.command(help='Generates and displays an inspiring image')
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

bot.add_cog(roll.Roll())
bot.add_cog(audio.Audio())
bot.run(TOKEN)