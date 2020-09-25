import datetime
import discord
import json

client = discord.Client()

y2020 = {
    "2020-08-31": "7568",
    "2020-09-25": "7568",
    "2020-10-23": "7568",
    "2020-11-25": "7568",
    "2020-12-23": "7568",
    "2021-01-18": "7568",
    "2021-02-25": "7568",
    "2021-03-25": "7568",
    "2021-04-23": "7568",
    "2021-05-25": "7568"
}


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$eval'):
        await message.channel.send(eval(message.content[5:]))

data = json.load(open('config.json',))
client.run(data['token'])
