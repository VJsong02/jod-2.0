import datetime
import discord
from discord.ext import tasks, commands
from itertools import cycle
import json
import os
import threading
import time
import traceback

client = commands.Bot("$")
embedchannel = 758774618546503700

dates = {
    datetime.date(2020,  8, 31): 7568,
    datetime.date(2020,  9, 25): 7568,
    datetime.date(2020, 10, 23): 7568,
    datetime.date(2020, 11, 25): 7568,
    datetime.date(2020, 12, 23): 7568,
    datetime.date(2021,  1, 18): 11352,
    datetime.date(2021,  2, 25): 7568,
    datetime.date(2021,  3, 25): 7568,
    datetime.date(2021,  4, 23): 7568,
    datetime.date(2021,  5, 25): 3784,
    datetime.date(2021,  6, 25): 0,
    datetime.date(2021,  7, 25): 0
}

interests = {
    2020: 1.0016,
    2021: 1.0016
}


def calc_payments(now=datetime.date.today()):
    sum = 0
    for (date, amt) in dates.items():
        if(date <= now):
            if amt > 0:
                sum += amt + 3292
    return sum


def calc_debt(now=datetime.date.today(), interest=interests):
    sum = 0
    for (date, amt) in dates.items():
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


async def send_embed(embed, client=client, channel=embedchannel):
    await client.get_channel(channel).send(embed)


@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="dina lån"
        )
    )
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == 'lån?':
        await message.channel.send(embed=gen_embed())

    if message.content.startswith("$eval"):
        try:
            print(message.author.id, message.content[6:])
            await message.channel.send(eval(message.content[6:]))
        except Exception:
            await message.channel.send("```" + traceback.format_exc() + "```")


@tasks.loop(minutes=1)
async def timer():
    await client.wait_until_ready()
    day = datetime.date.today()
    now = datetime.datetime.now()
    if day in dates and now.minute == 0 and now.hour == 0:
        print("Sent embed at", now)
        await client.get_channel(embedchannel).send(embed=gen_embed())

timer.start()
data = json.load(open('config.json',))
client.run(data['token'])
