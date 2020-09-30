import datetime
import discord
from discord.ext import tasks, commands
from itertools import cycle
import json
import os

client = commands.Bot(command_prefix="$")
status = cycle(["on", "off"])

loans = {
    datetime.datetime(2020,  8, 31): 7568,
    datetime.datetime(2020,  9, 25): 7568,
    datetime.datetime(2020, 10, 23): 7568,
    datetime.datetime(2020, 11, 25): 7568,
    datetime.datetime(2020, 12, 23): 7568,
    datetime.datetime(2021,  1, 18): 11352,
    datetime.datetime(2021,  2, 25): 7568,
    datetime.datetime(2021,  3, 25): 7568,
    datetime.datetime(2021,  4, 23): 7568,
    datetime.datetime(2021,  5, 25): 3784,
    datetime.datetime(2021,  6, 25): 0,
    datetime.datetime(2021,  7, 25): 0
}

interests = {
    2020: 1.0016,
    2021: 1.0016

}


def calc_payments(now=datetime.datetime.now()):
    sum = 0
    for (date, amt) in loans.items():
        if(date <= now):
            if amt > 0:
                sum += amt + 3292
    return sum


def calc_debt(now=datetime.datetime.now(), interest=interests):
    sum = 0
    for (date, amt) in loans.items():
        if(date <= now):
            sum *= (interest[now.year] ** (1 / 12))
            sum += amt
    return sum


def gen_embed():
    embed = discord.Embed(
        title="CSN",
        colour=discord.Colour.orange()
    )
    embed.add_field(name="Utbetalat", value=str(calc_payments()) +
                    str(" kr"), inline=False)
    embed.add_field(name="Skuld", value=str(round(
        calc_debt(), 2)) + str(" kr"), inline=False)
    return embed

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$setpresence'):
        await client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="dina lån"
                )
            )

    if message.content.startswith('$eval'):
        print(message.author.id, message.content[6:])
        await message.channel.send(eval(message.content[6:]))

    if message.content.startswith('$exec'):
        print(message.author.id, message.content[6:])
        await message.channel.send(exec(message.content[6:]))

    if message.content == 'lån?':
        await message.channel.send(embed=gen_embed())

@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

data = json.load(open('config.json',))
client.run(data['token'])
