import io
import json
import matplotlib
import numpy as np
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
    # 2020 - 2021
    date(2020,  8, 31): (7568,  3292 - 150),  # uppläggningsavgift
    date(2020,  9, 25): (7568,  3292),
    date(2020, 10, 23): (7568,  3292),
    date(2020, 11, 25): (7568,  3292),
    date(2020, 12, 23): (7592,  3302),
    date(2021,  1, 18): (11424, 4968 - 150),  # uppläggningsavgift
    date(2021,  2, 25): (7616,  3312),
    date(2021,  3, 25): (7616,  3312),
    date(2021,  4, 23): (7616,  3312),
    date(2021,  5, 25): (3808,  1656),
    
    # 2021 - 2022
    date(2021,  8, 30): (7616,  3312 - 150),  # uppläggningsavgift
    date(2021,  9, 24): (7616,  3312),
    date(2021, 10, 25): (7616,  3312),
    date(2021, 11, 25): (7616,  3312),
    date(2021, 12, 23): (7616,  3312),
    date(2022,  1, 17): (11424, 4968 - 150),  # uppläggningsavgift
    date(2022,  2, 25): (7616,  3312),
    date(2022,  3, 25): (7616,  3312),
    date(2022,  4, 25): (7616,  3312),
    date(2022,  5, 25): (3808,  1656),
}

interests = {
    2020: 1.0016,
    2021: 1.0005
}


def calc_debt(now=None):
    if(now == None):
        now = date.today()
    loaned = 0
    owe = 0
    granted = 0
    prevday = None
    for (day, (loan, grant)) in list(payments.items())+[(now, (0, 0))]:
        if(day <= now):
            if(prevday):
                if(prevday.year == day.year):
                    owe *= (interests[day.year] ** ((day-prevday).days / 365))
                else:
                    newyear = date(day.year-1, 12, 31)
                    owe *= (interests[day.year] ** ((day-newyear).days / 365)) * (interests[prevday.year] ** ((newyear-prevday).days / 365))
            owe += loan
            loaned += loan
            granted += grant
            prevday = day
    return (loaned, owe, granted)


def gen_embed():
    loaned, owe, granted = calc_debt()

    embed = discord.Embed(
        title="CSN informerar",
        colour=discord.Colour.from_rgb(60, 34, 92)
    )
    embed.add_field(name="Utbetalat", value=str(
        loaned + granted) + " kr", inline=False)
    embed.add_field(name="Skuld", value=str(round(
        owe, 2)) + " kr (varav " + str(round(owe-loaned, 2)) + " kr ränta)", inline=False)
    for day in payments:
        if(day > date.today()):
            dt = datetime.combine(day, datetime.min.time()) - datetime.now()
            s = f"{dt.seconds//3600:02d}:{dt.seconds//60%60:02d}:{dt.seconds%60:02d}"
            if(dt.days == 1):
                s = "en dag och " + s
            elif(dt.days > 1):
                s = f"{dt.days} dagar och " + s
            embed.add_field(name="Nästa utbetalning",
                            value=str(day) + " (om " + s + ")")
            break

    motivational_texts = [
        "Nu känner du dig inte lika rik längre va!?",
        "Ränta-på-ränta is coming for you!",
        "Hjälp med skuldsanering kostar bara 995 kr / timme.",
        "Inte långt till personlig konkurs grabben!",
        "Ett omöjligt fall för kronofogden...",
        "Du är en lat drulle! /Johan Grudemo"
    ]
    embed.add_field(name="Motiverande text", value=random.choice(
        motivational_texts), inline=False)
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

    if message.content.startswith("$wa"):
        query = message.content[3:].strip()
        url = "http://api.wolframalpha.com/v1/simple?appid={}&units=metric&i={}"\
            .format(json.load(open('config.json',))['wolfram'], urllib.parse.quote(query))
        await message.channel.send(file=discord.File(io.BytesIO(requests.get(url).content), "result.png"))

    if message.content.startswith("$math"):
        buffer = io.BytesIO()
        properties = font_manager.FontProperties(size=36)

        mathtext.math_to_image("${}$".format(message.content[5:].strip()
            .replace("\n", "").replace("`", "")), buffer, format="png",
            prop=properties, dpi=96)
        buffer.seek(0)
        im = Image.open(buffer)
        image_data = np.asarray(im)
        image_data_bw = image_data.max(axis=2)
        non_empty_columns = np.where(image_data_bw.max(axis=0)>0)[0]
        non_empty_rows = np.where(image_data_bw.max(axis=1)>0)[0]
        cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))
        image_data_new = image_data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 , :]
        wx = 1
        wc = 10
        hx = 1
        hc = 10
        im = Image.fromarray(image_data_new)
        new_size = (int(im.size[0] * wx + wc * 2),\
            int(im.size[1] * hx + hc * 2))
        img = Image.new("RGB", new_size, (255, 255, 255))
        img.paste(im, ((new_size[0]-im.size[0])//2,
                       (new_size[1]-im.size[1])//2))
        
        newbuffer = io.BytesIO()
        img.save(newbuffer, format="PNG")
        newbuffer.seek(0)

        await message.channel.send(file=discord.File(newbuffer, "maths.png"))


@tasks.loop(minutes=1)
async def timer():
    await client.wait_until_ready()
    day = date.today()
    now = datetime.now()
    if day in payments and now.minute == 0 and now.hour == 0:
        await main_channel.send(embed=gen_embed())

matplotlib.rcParams['mathtext.fontset'] = 'cm'
data = json.load(open('config.json',))
client.run(data['token'])
