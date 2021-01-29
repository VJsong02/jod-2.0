import io
import json
import os
import random
import threading
import time
import traceback
import urllib
from datetime import date, datetime
from matplotlib import mathtext, font_manager
from itertools import cycle

import discord
import requests
from discord.ext import commands, tasks
from matplotlib import mathtext, pyplot
from PIL import Image

client = commands.Bot("$")
main_channel = None

payments = {
    date(2020,  8, 31): (7568,  3292 - 150), #uppläggningsavgift
    date(2020,  9, 25): (7568,  3292), 
    date(2020, 10, 23): (7568,  3292),
    date(2020, 11, 25): (7568,  3292),
    date(2020, 12, 23): (7592,  3302),
    date(2021,  1, 18): (11424, 4968 - 150), #uppläggningsavgift
    date(2021,  2, 25): (7616,  3312),
    date(2021,  3, 25): (7616,  3312),
    date(2021,  4, 23): (7616,  3312),
    date(2021,  5, 25): (3808,  1656),
    date(2021,  6, 25): (0,     0),
    date(2021,  7, 25): (0,     0)
}

interests = {
    2020: 1.0016,
    2021: 1.0005
}


def calc_debt(now=None):
    if(now == None): now = date.today()
    loaned = 0
    owe = 0
    granted = 0
    for (day, (loan, grant)) in payments.items():
        if(day <= now):
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
    for day in payments:
        if(day > date.today()):
            dt = datetime.combine(day, datetime.min.time()) - datetime.now()
            s = f"{dt.seconds//3600:02d}:{dt.seconds//60%60:02d}:{dt.seconds%60:02d}"
            if(dt.days == 1): s = "en dag och " + s
            elif(dt.days > 1): s = f"{dt.days} dagar och " + s
            embed.add_field(name="Nästa utbetalning", value=str(day) + " (om " + s + ")")
            break
    
    motivational_texts = [
        "Nu känner du dig inte lika rik längre va!?",
        "Ränta-på-ränta is coming for you!",
        "Hjälp med skuldsanering kostar bara 995 kr / timme.",
        "Inte långt till personlig konkurs grabben!",
        "Ett omöjligt fall för kronofogden...",
        "Du är en lat drulle! /Johan Grudemo"
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
            
    if message.content.startswith("$wa"):
        query = message.content[3:].strip()
        url = "http://api.wolframalpha.com/v1/simple?appid={}&units=metric&i={}"\
            .format(json.load(open('config.json',))['wolfram'],urllib.parse.quote(query))
        await message.channel.send(file=discord.File(io.BytesIO(requests.get(url).content), "result.png"))

    if message.content.startswith("$math"):
        buffer = io.BytesIO()
        properties = font_manager.FontProperties(size=24)
        
        mathtext.math_to_image("${}$".format(message.content[5:].strip()\
            .replace("\n", "")).replace("`", ""), buffer, format="png",\
                prop=properties, dpi=384)
        buffer.seek(0)
        
        await message.channel.send(file=discord.File(buffer, "maths.png"))

@tasks.loop(minutes=1)
async def timer():
    await client.wait_until_ready()
    day = date.today()
    now = datetime.now()
    if day in payments and now.minute == 0 and now.hour == 0:
        await main_channel.send(embed=gen_embed())

data = json.load(open('config.json',))
client.run(data['token'])
