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
    datetime.datetime(2021,  5, 25): 3784
}

def calc_debt():
    sum = 0
    for (date, amt) in loans.items():
        if(date <= datetime.datetime.now()):
            sum += amt
    return sum

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$eval'):
        await message.channel.send(eval(message.content[5:]))
    
    if message.content == 'lån?':
        await message.channel.send("Du har -" + str(calc_debt()) + " kr")

data = json.load(open('config.json',))
client.run(data['token'])
