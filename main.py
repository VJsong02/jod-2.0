from datetime import date
from datetime import datetime
import discord
from discord.ext import tasks, commands
from itertools import cycle
import json
import os
import threading
import time
import traceback
import random

client = commands.Bot("$")
main_channel = None

payments = {
    date(2020,  8, 31): (7568,  3292),
    date(2020,  9, 25): (7568,  3292 - 150), #150 kr uppläggningsavgift
    date(2020, 10, 23): (7568,  3292),
    date(2020, 11, 25): (7568,  3292),
    date(2020, 12, 23): (7568,  3292),
    date(2021,  1, 18): (11352, 4938 - 150), #uppläggningsavgift
    date(2021,  2, 25): (7568,  3292),
    date(2021,  3, 25): (7568,  3292),
    date(2021,  4, 23): (7568,  3292),
    date(2021,  5, 25): (3784,  1646),
    date(2021,  6, 25): (0,     0),
    date(2021,  7, 25): (0,     0)
}

interests = {
    2020: 1.0016,
    2021: 1.0016  # (?)
}


def calc_debt(now=date.today()):
    loaned = 0
    owe = 0
    granted = 0
    for (date, (loan, grant)) in payments.items():
        if(date <= now):
            owe *= (interests[now.year] ** (1 / 12))
            owe += loan
            loaned += loan
            granted += grant
    return (loaned, owe, granted)


def gen_embed():
    loaned, owe, granted = calc_debt()

    embed = discord.Embed(
        title="CSN informerar",
        colour=discord.Colour.from_rgb(60, 34, 92)
    )
    embed.add_field(name="Utbetalat", value=str(loaned + granted) + " kr", inline=False)
    embed.add_field(name="Skuld", value=str(round(owe, 2)) + " kr (varav " + str(round(owe-loaned, 2)) + " kr ränta)", inline=False)
    for date in payments:
        if(date > date.today()):
            dt = datetime.combine(date, datetime.min.time()) - datetime.now()
            s = f"{dt.seconds//3600:02d}:{dt.seconds//60%60:02d}:{dt.seconds%60:02d}"
            if(dt.days == 1): s = "en dag och " + s
            elif(dt.days > 1): s = f"{dt.days} dagar och " + s
            embed.add_field(name="Nästa utbetalning", value=str(date) + " (om " + s + ")")
            break
    
    motivational_texts = [
        "Nu känner du dig inte lika rik längre va!?",
        "Ränta-på-ränta is coming for you!",
        "Hjälp med skuldsanering kostar bara 995 kr / timme.",
        "Inte långt till personlig konkurs grabben!",
        "Ett omöjligt fall för kronofogden...",
        "Nu får du faktiskt börja jobba din lata drulle! /Johan Grudemo"
    ]
    embed.add_field(name="Motiverande text", value=random.choice(motivational_texts), inline=False)
    return embed


async def send_embed(embed, client=client, channel=main_channel):
    await client.get_channel(channel).send(embed)


@client.event
async def on_ready():
    global main_channel
    main_channel = client.get_channel(748580468550533232)
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="dina lån"
        )
    )
    print('Logged in as {0.user}'.format(client))
    timer.start()


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
    day = date.today()
    now = datetime.now()
    if day in payments and now.minute == 0 and now.hour == 0:
        await main_channel.send(embed=gen_embed())


data = json.load(open('config.json',))
client.run(data['token'])
