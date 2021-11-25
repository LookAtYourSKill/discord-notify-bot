# imports

import json
import datetime

import asyncio
import discord
import requests
from discord.ext import commands
from discord.ext.tasks import loop

from twitch import get_notifications
from twitch import get_streams
from twitch import get_users

# open the config.json file to get the information from it
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())
bot.remove_command('help')


# start when bot start
@bot.event
async def on_ready():
    print(f'Botid: {bot.user.id} - Name: {bot.user.name}#{bot.user.discriminator}')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f'$ping | to check if im alive'),
        status=discord.Status.online)


# ping command
@bot.command()
async def ping(ctx):
    embed = discord.Embed(description=f'Pong | My Ping: **{round(bot.latency * 1000)}ms**')
    await ctx.send(embed=embed)


# help command
@bot.command()
async def help(ctx):
    embed = discord.Embed(description=f'Help Command | My Ping: **{round(bot.latency * 1000)}ms**',
                          color=discord.Color.blurple(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name='__$streamer__',
                    value='`Display all streamer, which are watched`\n'
                          '\n'
                          '**Aliases:** ``watchlist``',
                    inline=False)
    embed.add_field(name='__$addstreamer [streamer_name]__',
                    value='`Add a streamer to the watchlist`\n'
                          '\n'
                          '**Aliases:** ``streameradd, add``',
                    inline=False)
    embed.add_field(name='__$removestreamer [streamer_name]__',
                    value='`Remove a streamer from the watchlist`\n'
                          '\n'
                          '**Aliases:** ``streamerremove, rm, remove``',
                    inline=False)
    embed.add_field(name='$streamcheck',
                    value='`Check all streams, within one message`\n'
                          '\n'
                          '**Aliases:** ``checkstreams, streamcheck``',
                    inline=False)
    embed.add_field(name='__$ping__',
                    value='`Get the Ping from the bot`\n'
                          '\n'
                          '**Aliases:** ``/``',
                    inline=False)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text='verpflichtend -> [] | <> <- freiwillig')
    await ctx.send(embed=embed)


@bot.command(name='check_streams_one_message', aliases=['streamcheck', 'checkstreams'])
@commands.is_owner()
async def check_streams_one_message(ctx):
    users = get_users(config["watchlist"])
    streams = get_streams(users)

    embed = discord.Embed(title='Who is Live?')
    for stream in streams.values():
        if not stream:
            embed.add_field(name='__Nobody is Live!__', value='No streamer from your watchlist is live!')
            await ctx.send(embed=embed)
        else:
            embed.add_field(name=f'Name : {stream["user_name"]}',
                            value=f'**Type :** ``{stream["type"]}``\n'
                                  f'**Title :** __{stream["title"]}__\n'
                                  f'**Link :** https://www.twitch.tv/{stream["user_login"]}',
                            inline=False)
    await ctx.send(f'{ctx.author.mention} Dein Stream Check. Es sind insgesamt **{len(streams)} Streamer Live!**',
                   embed=embed)


@bot.command(name='addstreamer', aliases=['add_streamer', 'streamer_add', 'streameradd'])
@commands.is_owner()
async def addstreamer(ctx, streamer):
    if not streamer:
        missing_streamer_embed = discord.Embed(description=f'**Bitte gebe ein Streamer an.**')
        await ctx.send(embed=missing_streamer_embed)

    with open('config.json', 'r') as f:
        data = json.load(f)

        if streamer in data["watchlist"]:
            embed = discord.Embed(title='<:close:864599591692009513> ERROR',
                                  description=f'`Der Streamer ({streamer})` ist **bereits in der Watchlist!**')
            await ctx.send(embed=embed, delete_after=5)
            await ctx.message.delete()
            return

        else:

            data["watchlist"].append(streamer)

    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)

        embed = discord.Embed(title='',
                              description='')
        embed.add_field(name='<:open:869959941321011260> Watchlist Add',
                        value=f'Hinzugefügter Streamer:\n'
                              f'`{streamer}`',
                        inline=False)

        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()


@bot.command(name='removestreamer', aliases=['rmstreamer', 'rm_streamer'])
@commands.is_owner()
async def remove_streamer(ctx, streamer):
    if not streamer:
        missing_streamer_embed = discord.Embed(description=f'**Bitte gebe ein Streamer an.**')
        await ctx.send(embed=missing_streamer_embed)

    with open("config.json", "r") as f:
        data = json.load(f)

        if streamer not in data["watchlist"]:
            embed = discord.Embed(title='<:close:864599591692009513> ERROR',
                                  description=f'`Der Streamer ({streamer})` ist **nicht in der Watchlist!**')
            await ctx.send(embed=embed, delete_after=5)
            await ctx.message.delete()
            return

        else:

            data["watchlist"].remove(streamer)

    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)

        embed = discord.Embed(title='',
                              description='')
        embed.add_field(name='<:open:869959941321011260> Watchlist Remove',
                        value=f'**Entfernter Streamer:**\n'
                              f'`{streamer}`',
                        inline=False)

        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()


@bot.command(name='streamer', aliases=['watchlist'])
async def streamer(ctx):
    with open('config.json', 'r') as f:
        data = json.load(f)

        watchlist = data["watchlist"]

        if not watchlist:
            embed = discord.Embed(title='',
                                  description='')
            embed.add_field(name='<:close:864599591692009513> **ERROR**',
                            value='`Es ist kein Streamer auf der Watchlist!`',
                            inline=False)
            await ctx.send(embed=embed)

        else:

            embed = discord.Embed(title='',
                                  description='')
            embed.add_field(name='Streamer Watchlist',
                            value=f'`{data["watchlist"]}`',
                            inline=False)
            await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title='<:close:864599591692009513> ERROR',  # (CommandNotFound)
                              description=f'`Der Command konnte nicht gefunden werden!`. Bitte versuche es erneut!',
                              color=ctx.author.colour)
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()

    else:
        await ctx.send(f'__Unknown Error__... Here it is\n'
                       f'```py\n'
                       f'{error}\n'
                       f'```')

@loop(seconds=90)
async def check_twitch_online_streamers():
    # get the channel, where to post the message
    channel = bot.get_channel(config["notify_channel"])

    # when the channel is not there, return
    if not channel:
        return

    # get the notification method
    notifications = get_notifications()
    for notification in notifications:
        # send the message with the notification in the channel

        embed = discord.Embed(title=f'__{notification["title"]}__',
                              url=f'https://twitch.tv/{notification["user_login"]}',
                              timestamp=datetime.datetime.utcnow(),
                              color=discord.Color.purple())
        embed.add_field(
            name=f'Playing {notification["game_name"]} for {notification["viewer_count"]} viewer!',
            value=f'[Click here](https://twitch.tv/{notification["user_login"]})')
        # embed.add_field(
        #    name=f'Streaming for {notification["viewer_count"]} viewer',
        #    value=f'[go to Stream](https://twitch.tv/{notification["user_login"]})')
        embed.set_author(
            name=f'{notification["user_name"]} ist Live auf Twitch!',
            url=f'https://twitch.tv/{notification["user_login"]}')
        embed.set_image(
            url=f'https://static-cdn.jtvnw.net/previews-ttv/live_user_{notification["user_login"]}-1920x1080.jpg')
        embed.set_footer(text=f'Discord Notify Bot')
        await asyncio.sleep(5)
        await channel.send(f'||@everyone|| {notification["user_name"]} ist Live!\n'
                           f'https://twitch.tv/{notification["user_login"]}', embed=embed)


if __name__ == "__main__":
    check_twitch_online_streamers.start()
    bot.run(config["discord_token"], reconnect=True)
