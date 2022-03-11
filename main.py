import json
import datetime
from textwrap import dedent

import asyncio
import disnake
from disnake.ext import commands
from disnake.ext.tasks import loop

from twitch import get_notifications
from twitch import get_streams
from twitch import get_users
from twitch import get_profile_image


running = False


bot = commands.Bot(command_prefix='tv!', intents=disnake.Intents.all())
bot.remove_command('help')



@bot.event
async def on_ready():
    global running
    print('>----------------------------------------------------------------------<')
    print(f'Botid: {bot.user.id} - Name: {bot.user.name}#{bot.user.discriminator}')
    print('>----------------------------------------------------------------------<')
    if not running:
        check_twitch_online_streamers.start()
        running = True
    await bot.change_presence(
        activity=disnake.Activity(
            type=disnake.ActivityType.watching,
            name='tv!ping | to check if im alive'),
        status=disnake.Status.online)



@bot.command()
async def ping(ctx):
    embed = disnake.Embed(description=f'Pong | My Ping: **{round(bot.latency * 1000)}ms**')
    await ctx.send(embed=embed)



@bot.command()
async def help(ctx):
    embed = disnake.Embed(
        description=f'Help Command | My Ping: **{round(bot.latency * 1000)}ms**',
        color=disnake.Color.blurple(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(
        name='__tv!streamer__',
        value=dedent(
            """
                `Display all streamer, which are watched`
                **Aliases:** ``watchlist``
            """
        ),
        inline=False
    )
    embed.add_field(
        name='__tv!addstreamer [streamer_name]__',
        value=dedent(
            """
                `Add a streamer to the watchlist`
                **Aliases:** ``streameradd, add, add_streamer``
            """
        ),
        inline=False
    )
    embed.add_field(
        name='__tv!removestreamer [streamer_name]__',
        value=dedent(
            """
                `Remove a streamer from the watchlist`
                **Aliases:** ``streamerremove, rm, remove``
            """
        ),
        inline=False
    )
    embed.add_field(
        name='__tv!streamcheck__',
        value=dedent(
            """
                `Check all streams, within one message`
                **Aliases:** ``checkstreams, streamcheck, check``
            """
        ),
        inline=False
    )
    embed.add_field(
        name='__tv!ping__',
        value=dedent(
            """
                `Get the Ping from the bot`
                **Aliases:** ``/``
            """
        ),
        inline=False
    )
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text='verpflichtend -> [] | <> <- freiwillig')
    await ctx.send(embed=embed)


@bot.command(
    name='check_streams_one_message',
    aliases=['streamcheck', 'checkstreams', 'check']
)
async def check_streams_one_message(ctx):

    with open('data.json', 'r', encoding='UTF-8') as data_file:
        data_file = json.load(data_file)

    users = get_users(data_file["watchlist"])
    streams = get_streams(users)

    embed = disnake.Embed(color=disnake.Color.purple())
    embed.set_author(
        name='Who is Live?',
        icon_url='https://static-cdn.jtvnw.net/jtv_user_pictures/8a6381c7-d0c0-4576-b179-38bd5ce1d6af-profile_image-300x300.png',
        url='https://twitch.tv'
    )
    embed.set_thumbnail(
        url='https://static-cdn.jtvnw.net/jtv_user_pictures/8a6381c7-d0c0-4576-b179-38bd5ce1d6af-profile_image-300x300.png'
    )
    if streams:
        for stream in streams.values():

            embed.add_field(
                name=f'Name : {stream["user_name"]}',
                value=dedent(
                    f"""
                        **Title :** __{stream["title"]}__
                        **Viewer :** ``{stream["viewer_count"]}``
                        **Game :** ``{stream["game_name"]}``
                        **Streamt seit:** ``{stream["started_at"][11:][:5]} Uhr am {stream["started_at"][8:][:2]}.{stream["started_at"][5:][:2]}.{stream["started_at"][:4]}``
                        **Link :** https://www.twitch.tv/{stream["user_login"]}
                        >-------------------------------------------------------------------------<
                    """
                ),
                inline=False
            )
    else:
        embed.add_field(
            name='__Nobody is Live!__',
            value='No streamer from your watchlist is live!',
            inline=False
        )

    if len(streams) == 1:
        await ctx.send(
            f"{ctx.author.mention} Dein Stream Check. Es ist **1 Streamer Live!**",
            embed=embed
        )
    else:
        await ctx.send(
            f"{ctx.author.mention} Dein Stream Check. Es sind insgesamt **{len(streams)} Streamer Live!**",
            embed=embed
        )


@bot.command(name='addstreamer', aliases=['streameradd', 'add'])
@commands.is_owner()
async def addstreamer(ctx, add_streamer=None):

    with open('data.json', 'r', encoding='UTF-8') as data_file:
        data = json.load(data_file)

    if not add_streamer:
        missing_streamer_embed = disnake.Embed(
            description='**Bitte gebe ein Streamer an.**',
            color=disnake.Color.red()
        )
        await ctx.send(embed=missing_streamer_embed, delete_adter=5)
        await ctx.message.delete()
        return

    elif add_streamer in data["watchlist"]:
        embed = disnake.Embed(
            title=':x: ERROR',
            description=f'`Der Streamer ({add_streamer})` ist **bereits in der Watchlist!**',
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()
        return
    else:
        data["watchlist"].append(add_streamer.lower())
        with open("data.json", "w", encoding='UTF-8') as data_file:
            json.dump(data, data_file, indent=4)

        embed = disnake.Embed(
            title=':white_check_mark: Watchlist Add',
            descripton=dedent(
                f"""
                    Hinzugefügter Streamer:
                    `{add_streamer}`
                """
            ),
            color=disnake.Color.green()
        )
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()
        return


@bot.command(name='removestreamer', aliases=['rm', 'remove'])
@commands.is_owner()
async def remove_streamer(ctx, removestreamer=None):

    with open('data.json', 'r', encoding='UTF-8') as data_file:
        data = json.load(data_file)

    if not removestreamer:
        missing_streamer_embed = disnake.Embed(
            description='**Bitte gebe ein Streamer an.**',
            color=disnake.Color.red()
        )
        await ctx.send(embed=missing_streamer_embed, delete_after=5)
        await ctx.message.delete()
        return

    elif removestreamer not in data["watchlist"]:
        embed = disnake.Embed(
            title=':x: ERROR',
            description=f'`Der Streamer ({removestreamer})` ist **nicht in der Watchlist!**',
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()
        return
    else:
        data["watchlist"].remove(removestreamer.lower())

        with open("data.json", "w", encoding='UTF-8') as data_file:
            json.dump(data, data_file, indent=4)

        embed = disnake.Embed(
            title=':white_check_mark: Watchlist Remove',
            description=dedent(
                f"""
                    **Entfernter Streamer:**
                    `{removestreamer}`
                """
            ),
            color=disnake.Color.green()
        )
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()


@bot.command(name='streamer', aliases=['watchlist'])
async def streamer(ctx):

    with open('data.json', 'r', encoding='UTF-8') as data_file:
        data = json.load(data_file)

    streamer_watchlist = data["watchlist"]

    if not streamer_watchlist:
        embed = disnake.Embed(
            title=':x: **ERROR**',
            description='`Es ist kein Streamer auf der Watchlist!`',
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete()
        return

    else:
        embed = disnake.Embed(
            title=':white_check_mark: Streamer Watchlist',
            description=f'`{data["watchlist"]}`',
            color=disnake.Color.green()
        )
        await ctx.send(embed=embed)
        return


@loop(seconds=90)
async def check_twitch_online_streamers():

    with open('data.json', 'r', encoding='UTF-8') as data_file:
        data = json.load(data_file)

    print('Starte Check')

    channel = bot.get_channel(data["notify_channel"])

    if channel is None:
        print('Es wurde kein Channel angegeben')

    notifications = get_notifications()
    profile_images = get_profile_image(data["watchlist"])

    for notification in notifications:
        embed = disnake.Embed(
            title=f'__{notification["title"]}__',
            description=dedent(
                f"""
                    Playing `{notification["game_name"]}` for **{notification["viewer_count"]}** viewer!
                    [Click here](https://twitch.tv/{notification["user_login"]})
                """
            ),
            url=f'https://twitch.tv/{notification["user_login"]}',
            timestamp=datetime.datetime.utcnow(),
            color=disnake.Color.purple()
        )
        embed.set_author(
            name=f'{notification["user_name"]} ist Live auf Twitch!',
            url=f'https://twitch.tv/{notification["user_login"]}',
            icon_url=profile_images[notification["user_login"]]
        )
        embed.set_thumbnail(url=profile_images[notification["user_login"]])
        embed.set_image(
            url=f'https://static-cdn.jtvnw.net/previews-ttv/live_user_{notification["user_login"]}-1920x1080.jpg'
        )

        await asyncio.sleep(5)
        await channel.send(
            f'||@everyone|| {notification["user_name"]} ist Live!\n'
            f'https://twitch.tv/{notification["user_login"]}', embed=embed
        )


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return

    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        if isinstance(error, commands.CommandNotFound):
            embed = disnake.Embed(
                description='**Unbekannter Command!** Überprüfe deine Eingabe mit `tv!help`',
                color=disnake.Color.red()
            )
            await ctx.send(embed=embed)

with open('config.json', 'r', encoding='UTF-8') as file:
    config = json.load(file)

if __name__ == "__main__":
    bot.run(config["discord_token"], reconnect=True)
    bot.wait_until_ready()
