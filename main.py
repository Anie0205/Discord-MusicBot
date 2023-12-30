import asyncio
import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import youtube_dl

token = "MTE5MDM0ODYwNTA5ODMxNTc3Ng.G9v9iH.C-Jkzp7mZZQye-kb1HRyDZcYmNopHwrMLlcM3o"
load_dotenv()
DISCORD_TOKEN = os.getenv(token)

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!",intents=intents)

#To download the audiofile from Youtube
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
     'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume = 0.5):
        super().__init__(source, volume)
        self.data=data
        self.title = data.get('title')
        self.url = ''

    @classmethod
    async def from_url(cls, url, *, loop = None, stream = False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data :
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
    
#To make the bot join the voice channel
@bot.command(name = 'join')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect() 

@bot.command(name = 'play_song')
async def play(ctx,url):
    server = ctx.message.guild
    voice_channel = server.voice_channel
    async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop = bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(executable=r"C:\Users\anany\Desktop\Anie\Personal_projects\DiscordMusicBot\ffmpeg-2023-12-28-git-c1340f3439-full_build\bin", source = filename))
    await ctx.send('**Now Playing:** {}',format(filename))

@bot.command(name = 'pause')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot has paused the music or it's not playing anything")

@bot.command(name = 'resume')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot is not playing songs")

@bot.command(name ='leave')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot has not joined any voice channel")

@bot.command(name ='stop')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything")

if __name__ == "__main__":
    bot.run(token)

