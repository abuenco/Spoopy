""" Spoopy Discord Bot """

import os
import discord
from discord.ext import commands

# Spoopy functions from funcs.py
import funcs as f

# Bot Setup
# For running locally, load token from .env file.
if not os.environ.get("DISCORD_TOKEN"):
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    
# For running on Heroku, load token from config vars.
else:
    TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents().all()
client = discord.Client(intent=intents)
bot = commands.Bot(command_prefix=".",intents=intents)

# Notify when the bot is connected to Discord.
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

# Spoopy Bot Commands
@bot.group(help="Commands for Spoopy")
async def spoopy(ctx):
    """ Initializes "spoopy" master command for bot.
    This was done to make it easier for users to distinguish 
    commands for different bots in a server given the same command prefix.
    """
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title = "Invalid spoopy command passed",
            description = "Enter *.spoopy help* to see WikiWally commands.",
            color = 0xFAD02C
            )
        embed.set_footer(
            text="Requested by: {}".format(ctx.author.display_name)
            )
        await ctx.channel.send(embed=embed)


# Spoopy sub commands
@spoopy.command(help="Gets information about an artist given a URL or query.")
async def artist(ctx, *, input):
    artist = f.get_artist(input)
    await ctx.channel.send(embed=f.embed_artist(ctx, artist))

@spoopy.command(help="Gets info about an album given a URL or query.")
async def album(ctx, *, input):
    album = f.get_album(input)
    await ctx.channel.send(embed=f.embed_album(ctx, album))

# NOTE: 'song' works the same way as 'track'. This command exists because
#        users are more likely to use 'song' than 'track' to describe
#        a song.
@spoopy.command(help="Searches for a song given a URL or query.")
async def song(ctx, *, input):
    track = f.get_track(input)
    await ctx.channel.send(embed=f.embed_track(ctx, track))

@spoopy.command(help="Searches for a track given a URL or query.")
async def track(ctx, *, input):
    track = f.get_track(input)
    await ctx.channel.send(embed=f.embed_track(ctx, track))

bot.remove_command("help")
@spoopy.command(help = "Help page for Spoopy Bot.")
async def help(ctx):
    """Returns the names and functions of Spoopy subcommands
    in an embed."""

    embed = discord.Embed(
            title = "Spoopy Bot Commands",
            description = "To use Spoopy Commands, \
                           enter ***.spoopy [command name]***", 
            color = 0xFAD02C
            )
    
    for c in spoopy.commands:
        embed.add_field(name=c.name, value=c.help, inline=False)

    embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
    await ctx.channel.send(embed=embed)

# Run the bot!
bot.run(TOKEN)