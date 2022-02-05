import json
import datetime

import asyncio
import discord
from discord.ext import commands
from discord.ext.tasks import loop

from twitch import get_notifications
from twitch import get_streams
from twitch import get_users
from twitch import get_profile_image

# -----------------------------------------------------------------------------------------------------------------------

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# -----------------------------------------------------------------------------------------------------------------------

bot = commands.Bot(command_prefix='tv!', intents=discord.Intents.all())
bot.remove_command('help')


# -----------------------------------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f'Botid: {bot.user.id} - Name: {bot.user.name}#{bot.user.discriminator}')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f'tv!ping | to check if im alive'),
        status=discord.Status.online)


# -----------------------------------------------------------------------------------------------------------------------

@bot.command()
async def ping(ctx):
    embed = discord.Embed(description=f'Pong | My Ping: **{round(bot.latency * 1000)}ms**')
    await ctx.send(embed=embed)


# -----------------------------------------------------------------------------------------------------------------------

@bot.command()
async def help(ctx):
    embed = discord.Embed(description=f'Help Command | My Ping: **{round(bot.latency * 1000)}ms**',
                          color=discord.Color.blurple(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name='__tv!streamer__',
                    value='`Display all streamer, which are watched`\n'
                          '**Aliases:** ``watchlist``',
                    inline=False)
    embed.add_field(name='__tv!addstreamer [streamer_name]__',
                    value='`Add a streamer to the watchlist`\n'
                          '**Aliases:** ``streameradd, add, add_streamer``',
                    inline=False)
    embed.add_field(name='__tv!removestreamer [streamer_name]__',
                    value='`Remove a streamer from the watchlist`\n'
                          '**Aliases:** ``streamerremove, rm, remove``',
                    inline=False)
    embed.add_field(name='__tv!streamcheck__',
                    value='`Check all streams, within one message`\n'
                          '**Aliases:** ``checkstreams, streamcheck, check``',
                    inline=False)
    embed.add_field(name='__tv!ping__',
                    value='`Get the Ping from the bot`\n'
                          '**Aliases:** ``/``',
                    inline=False)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text='verpflichtend -> [] | <> <- freiwillig')
    await ctx.send(embed=embed)


# -----------------------------------------------------------------------------------------------------------------------

@bot.command(name='check_streams_one_message', aliases=['streamcheck', 'checkstreams', 'check'])
@commands.is_owner()
async def check_streams_one_message(ctx):
    users = get_users(config["watchlist"])
    streams = get_streams(users)

    embed = discord.Embed(title='Who is Live?', color=discord.Color.purple())
    for stream in streams.values():
        if not streams:
            embed.add_field(name='__Nobody is Live!__', value='No streamer from your watchlist is live!', inline=False)
        else:
            embed.add_field(name=f'Name : {stream["user_name"]}',
                            value=f'**Title :** __{stream["title"]}__\n'
                                  f'**Viewer** : ``{stream["viewer_count"]}``\n'
                                  f'**Game** : ``{stream["game_name"]}``\n'
                                  f'**Link :** https://www.twitch.tv/{stream["user_login"]}',
                            inline=False)
    await ctx.send(
        f'{(f"{ctx.author.mention} Dein Stream Check. Es ist **1 Streamer Live!**" if len(streams) == 1 else f"{ctx.author.mention} Dein Stream Check. Es sind insgesamt **{len(streams)} Streamer Live!**")}',
        embed=embed)


# -----------------------------------------------------------------------------------------------------------------------

@bot.command(name='addstreamer', aliases=['streameradd', 'add'])
@commands.is_owner()
async def addstreamer(ctx, add_streamer=None):
    if not add_streamer:
        missing_streamer_embed = discord.Embed(description=f'**Bitte gebe ein Streamer an.**',
                                               color=discord.Color.red())
        await ctx.send(embed=missing_streamer_embed, delete_adter=5)
        await ctx.message.delete()
        return

    if streamer in config["watchlist"]:
        embed = discord.Embed(title=':x: ERROR',
                              description=f'`Der Streamer ({add_streamer})` ist **bereits in der Watchlist!**',
                              color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()
        return

    else:
        config["watchlist"].append(add_streamer)
        with open("config.json", "w") as file:
            json.dump(config, file, indent=4)

        embed = discord.Embed(title=':white_check_mark: Watchlist Add',
                              description=f'Hinzugefügter Streamer:\n'
                                          f'`{add_streamer}`',
                              color=discord.Color.green())
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()
        return


# -----------------------------------------------------------------------------------------------------------------------

@bot.command(name='removestreamer', aliases=['rm', 'remove'])
@commands.is_owner()
async def remove_streamer(ctx, removestreamer=None):
    if not removestreamer:
        missing_streamer_embed = discord.Embed(description=f'**Bitte gebe ein Streamer an.**',
                                               color=discord.Color.red())
        await ctx.send(embed=missing_streamer_embed, delete_after=5)
        await ctx.message.delete()
        return

    elif streamer not in config["watchlist"]:
        embed = discord.Embed(title=':x: ERROR',
                              description=f'`Der Streamer ({removestreamer})` ist **nicht in der Watchlist!**',
                              color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()
        return
    else:
        config["watchlist"].remove(streamer)
        with open("config.json", "w") as file:
            json.dump(config, file, indent=4)

        embed = discord.Embed(title=':white_check_mark: Watchlist Remove',
                              description=f'**Entfernter Streamer:**\n'
                                          f'`{removestreamer}`',
                              color=discord.Color.green())
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()


# -----------------------------------------------------------------------------------------------------------------------

@bot.command(name='streamer', aliases=['watchlist'])
async def streamer(ctx):
    streamer_watchlist = config["watchlist"]

    if not streamer_watchlist:
        embed = discord.Embed(title=':x: **ERROR**',
                              description='`Es ist kein Streamer auf der Watchlist!`',
                              color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()
        return

    else:

        embed = discord.Embed(title=':white_check_mark: Streamer Watchlist',
                              description=f'`{config["watchlist"]}`',
                              color=discord.Color.green())
        await ctx.send(embed=embed)
        return


# -----------------------------------------------------------------------------------------------------------------------

@loop(seconds=90)
async def check_twitch_online_streamers():
    channel = bot.get_channel(config["notify_channel"])

    if not channel:
        return

    notifications = get_notifications()
    profile_images = get_profile_image(config["watchlist"])

    for notification in notifications:
        for profile_image in profile_images:
            embed = discord.Embed(title=f'__{notification["title"]}__',
                                  description=f'Playing {notification["game_name"]} for **{notification["viewer_count"]}** viewer!\n'
                                              f'[Click here](https://twitch.tv/{notification["user_login"]})',
                                  url=f'https://twitch.tv/{notification["user_login"]}',
                                  timestamp=datetime.datetime.utcnow(),
                                  color=discord.Color.purple())
            embed.set_author(
                name=f'{notification["user_name"]} ist Live auf Twitch!',
                url=f'https://twitch.tv/{notification["user_login"]}',
                icon_url=profile_image["profile_image_url"])
            embed.set_thumbnail(url=f'{profile_image["profile_image_url"]}')
            embed.set_image(
                url=f'https://static-cdn.jtvnw.net/previews-ttv/live_user_{notification["user_login"]}-1920x1080.jpg')
            embed.set_footer(text=f'Twitch Notification')
            await asyncio.sleep(5)
            await channel.send(f'||@everyone|| {notification["user_name"]} ist Live!\n'
                               f'https://twitch.tv/{notification["user_login"]}', embed=embed)


# -----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    check_twitch_online_streamers.start()
    bot.run(config["discord_token"], reconnect=True)
