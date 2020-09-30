import datetime
import discord
import json

client = discord.Client()

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

def calc_debt(now=datetime.datetime.now(), interest=interests):
    sum = 0
    for (date, amt) in loans.items():
        if(date <= now):
            sum *= (interest[now.year] ** (1 / 12))
            sum += amt
    return sum

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$eval'):
        print(message.author.id, message.content[6:])
        await message.channel.send(eval(message.content[6:]))

    if message.content.startswith('$exec'):
        print(message.author.id, message.content[6:])
        await message.channel.send(exec(message.content[6:]))
    
    if message.content == 'lån?':
        await message.channel.send("Du har -"\
             + str(round(calc_debt(), 2)) + " kr")

data = json.load(open('config.json',))
client.run(data['token'])
