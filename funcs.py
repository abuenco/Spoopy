""" Functions for Spoopy 
This script contains all the bot's interactions with the
Spotipy API wrapper. 
"""

import os
import discord

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.client import SpotifyException

# Constant
color_spotify = 0x1DB954

# Spotify Client Setup
# For running locally, load Spotify Client Credentials from .env file.
if not (os.environ.get("SPOTIFY_CLIENT_ID") 
            and os.environ.get("SPOTIFY_CLIENT_SECRET")):
    from dotenv import load_dotenv
    load_dotenv()
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# For running on Heroku, load Spotify Client Credentials from config vars.
else:
    CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
        )
    )

### Functions for retrieval ###

def get_album(input):
    """ Returns the Album object that most closely matches the input.
    'None' is returned if no Album objects are found.
    """

    # This works when the input is a valid URI, URL, or ID.
    try:
        album = sp.album(input)
        return album

    # This runs when the input is a string.
    except SpotifyException:
        results = sp.search(input, type="album")

        try:
            album = results["albums"]["items"][0]
            return album

        # This runs when no results are found.
        except IndexError:
            return None
            
def get_artist(input):
    """ Returns the Artist object that most closely matches the input.
    'None' is returned if no Artist objects are found.
    """

    # This works when the input is a valid URI, URL, or ID.
    try:
        artist = sp.artist(input)
        return artist

    # This runs when the input is a string.
    except SpotifyException:
        results = sp.search(input, type="artist")

        try:
            artist = results["artists"]["items"][0]
            return artist
        
        # This runs when no results are found.
        except IndexError:
            return None

def get_track(input):
    """ Returns the Track object that most closely matches the input.
    'None' is returned if no Track objects are found.
    """

    # This works when the input is a valid URI, URL, or ID.
    try:
        track = sp.track(input)
        return track

    # This runs when the input is a string.
    except SpotifyException:
        results = sp.search(input, type="track")

        try:
            track = results["tracks"]["items"][0]
            return track

        # This runs when no results are found.
        except IndexError:
            return None

### Functions for parsing and Discord embedding ###

def embed_album(ctx, album):
    """ Parses an Album object and displays the info in a Discord embed.
    If album=None, an error message is displayed to the user.
    """

    try:
        name = album["name"]
        link = album["external_urls"]["spotify"]
        date = album["release_date"]
        track_total = album["total_tracks"]
        image = album["images"][0]["url"]

        # List all artists associated with an album.
        artists = album["artists"]
        artist_names = [artist['name'] for artist in artists]
        artist_urls = [artist["external_urls"]["spotify"] 
                        for artist in artists]

        # Done to hyperlink artist profiles in the embed.
        artist_info = ["["+artist_names[i]+"]("+artist_urls[i]+")"
                        for i in range(len(artist_names))]

        artist_info = ', '.join(artist_info)
        
        # Discord embed
        embed = discord.Embed(
            title = name,
            description=artist_info,
            url = link,
            color = color_spotify,
        )
        
        embed.set_image(url=image)

        embed.add_field(name="Release Date", value=date)
        embed.add_field(name="Tracks", value=track_total)

    # Thrown when album=None.
    except TypeError:
        embed = discord.Embed(
            title = "No albums found!",
            description = "Oh no, I couldn't find any albums! \
                          Please try a different URL, URI, or query.",
            color = color_spotify
        )

    embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
    return embed


def embed_artist(ctx, artist):
    """ Parses an Artist object and displays the info in a Discord embed.
    If artist=None, an error message is displayed to the user.
    """
    
    try:
        name = artist["name"]
        link = artist["external_urls"]["spotify"]
        genres = artist["genres"]
        genres = ", ".join(genres)
        images = artist["images"]
        artist_id = artist["id"]

        # List albums released by this artist.
        # Currently, only the 10 most recent albums are displayed.
        # This is due to the character limits in a Discord embed.
        albums = sp.artist_albums(artist_id, limit=10)["items"]
        album_names = [album["name"] for album in albums]
        album_urls  = [album["external_urls"]["spotify"] for album in albums]

        # Done to hyperlink artist profiles in the embed.
        album_info = ["["+ album_names[i] + "](" + album_urls[i] + ")" 
                      for i in range(len(album_names))]
        
        album_info = "\n".join(album_info)

        # Discord embed
        embed = discord.Embed(
            title = name,
            url = link,
            color = color_spotify,
        )

        # Include these fields only if the artist has genres or a profile image.
        if genres:
            embed.add_field(name="Genres",value=genres,inline=False)

        if images:
            img = images[0]["url"]
            embed.set_image(url=img)

        embed.add_field(name="Albums",value=album_info, inline=False)

    # Thrown when artist=None.
    except TypeError:
        embed = discord.Embed(
            title = "No artists found!",
            description = "Oh no, I couldn't find any artists! \
                          Please try a different URL, URI, or query.",
            color = color_spotify
        )
    embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
    return embed


def embed_track(ctx, track):
    """ Parses a Track object and displays the info in a Discord embed.
    If artist=None, an error message is displayed to the user.
    """

    try:
        name = track['name']
        link = track['external_urls']['spotify']
        track_num = track["track_number"]

        # List all artists associated with a track.
        artist_names = [artist['name'] for artist in track['artists']]
        artist_urls = [artist["external_urls"]["spotify"] 
                        for artist in track["artists"]]
        
        # Done to hyperlink artist profiles in the embed.
        artist_info = ["["+artist_names[i]+"]("+artist_urls[i]+")"
                        for i in range(len(artist_names))]

        artist_info = ', '.join(artist_info)

        # Album info
        album = track["album"]
        album_name = album["name"]
        album_url = album["external_urls"]["spotify"]
        album_date = album["release_date"]
        album_image = album['images'][0]['url']
        album_total = album["total_tracks"]

        # Discord embed
        embed = discord.Embed(
            title = name,
            url = link,
            description = artist_info,
            color = color_spotify,
        )

        embed.add_field(
            name="Album",
            value="[{}]({})".format(album_name, album_url),
            inline=True
            )

        embed.add_field(
            name="Release Date",
            value=album_date,
            inline=True
            )
        
        embed.add_field(
            name="Track", 
            value="{} out of {}".format(track_num, album_total),
            inline=True
            )
        
        embed.set_image(url=album_image)

    # Thrown when track=None.
    except TypeError:
        embed = discord.Embed(
            title = "No tracks found!",
            description = "Oh no, I couldn't find any tracks. Please try a different URL, URI, or query.",
            color = color_spotify
        )
    embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
    return embed