import discord
from discord.ext import commands
import aiohttp
import download_youtube

DOWNLOAD_PATH = 'downloads'

class Audio(commands.Cog):
    @commands.command(help='Plays audio from a Youtube video', usage='<url>')
    async def play(self, ctx, *args):
        if ctx.voice_client:
            if args:
                try:
                    await download_youtube.download(args[0], DOWNLOAD_PATH, ctx.guild)
                except Exception as e:
                    await ctx.send(f'Error: {e}')
                    return

                # Might use this later if I add a volume command 
                # source = discord.PCMVolumeTransformer(
                #     discord.FFmpegPCMAudio(
                #         f'{DOWNLOAD_PATH}/{ctx.guild}.webm',
                #         options='-vn'
                #     )
                # )
            
                ctx.voice_client.play(
                    discord.FFmpegOpusAudio(f'{DOWNLOAD_PATH}/{ctx.guild}.webm'), 
                    # source,
                    after=lambda e: ctx.voice_client.stop())
            else:
                if ctx.voice_client.is_paused():
                    ctx.voice_client.resume()
                else:
                    await ctx.send('You must provide a Youtube URL')

    @play.before_invoke
    async def ensure_voice(self, ctx):
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
    async def can_stop(self, ctx, is_pause):
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

    @commands.command(help='Pauses audio playback')
    async def pause(self, ctx):
        if await self.can_stop(ctx, True):
            ctx.voice_client.pause()

    @commands.command(help='Stops audio playback')
    async def stop(self, ctx):
        if await self.can_stop(ctx, False):
            ctx.voice_client.stop()

    @commands.command(aliases=['dc'], help='Disconnects the bot from voice')
    async def disconnect(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()