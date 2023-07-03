import random
from datetime import date, datetime

import discord
from discord.ext import commands, tasks

from csn import calc_debt, payments

client = commands.Bot("$")
main_channel = None
COLOUR = discord.Colour.from_rgb(60, 34, 92)

def get_quote():
    motivational_texts = [
        "Nu känner du dig inte lika rik längre va!?",
        "Ränta-på-ränta is coming for you!",
        "Hjälp med skuldsanering kostar bara 995 kr / timme.",
        "Inte långt till personlig konkurs grabben!",
        "Ett omöjligt fall för kronofogden...",
        "Du är en lat drulle! /Johan Grudemo"
    ]
    return random.choice(motivational_texts)

def gen_embed():
    loaned, owe, granted = calc_debt()

    embed = discord.Embed(
        title="CSN informerar",
        colour=COLOUR
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
                            value=str(sum(payments[day])) + " kr\n" 
                                + str(day) + " (om " + s + ")")
            break
    else:
        embed.add_field(name="Nästa utbetalning",
                        value="Ingen :pensive:")

    embed.add_field(name="Motiverande text", value=get_quote(), inline=False)
    return embed



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

    if message.content == 'utbetalningar?':
        dates = list(filter(lambda l: l > date.today(), payments))
        # print(dates)
        embed = discord.Embed(
            title="CSN informerar",
            colour=COLOUR
        )

        t = ""
        for k in dates:
            dt = datetime.combine(k, datetime.min.time()) - datetime.today()
            s = f"{dt.seconds//3600:02d}:{dt.seconds//60%60:02d}:{dt.seconds%60:02d}"
            if(dt.days == 1):
                s = "en dag och " + s
            elif(dt.days > 1):
                s = f"{dt.days} dagar och " + s
            t += f"{str(k)}: {sum(payments[k])} kr (om {s})\n"

        embed.add_field(name="Utbetalningar", value=t)
        embed.add_field(name="Motiverande text", value=get_quote(), inline=False)

        await message.channel.send(embed=embed)


@tasks.loop(minutes=1)
async def timer():
    await client.wait_until_ready()
    day = date.today()
    now = datetime.now()
    if day in payments and now.minute == 0 and now.hour == 0:
        await main_channel.send(embed=gen_embed())

