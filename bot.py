import discord
from discord.ext import commands
import emoji

import os
import ssl
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('SERVER_NAME')

num2words = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', \
             6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten', \
            11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', \
            15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen', \
            19: 'nineteen', 20: 'twenty', 30: 'thirty', 40: 'forty', \
            50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty', \
            90: 'ninety', 0: 'zero'}

movies = []

client = commands.Bot(command_prefix='$')

## TODO:
# Each member can only nominate one movie, clear out movies after vote is done
# DbD commands to choose killer
# Host this shit on AWS, Read in API Key in a safe way


@client.event
async def on_ready():
    server = discord.utils.get(client.guilds, name=SERVER)

    print(
        f'{client.user} is connected to the following guild: \n'
        f'{server.name}(id: {server.id})'
    )

    members = '\n - '.join([member.name for member in server.members])
    print(f'Guild members:\n - {members}')


@client.command(name='movie_vote')
async def movie_vote(ctx):
    server = discord.utils.get(client.guilds, name=SERVER)

    poll = '**Movie to Watch:**\n'
    count = 1

    for movie in movies:
        poll += f':{_num_to_word(count)}: {movie}\n'
        count += 1

    message = await ctx.send(poll)

    for i in range(1, len(movies) + 1):
        emoji = discord.utils.get(server.emojis, name=_num_to_word(i))
        await message.add_reaction(emoji)


@client.command(name='movie_nom')
async def movie_nominate(ctx, movie):
    if movie not in movies:
        movies.append(movie)


## Private Methods ##
def _num_to_word(num):
    try:
        return num2words[num]
    except KeyError:
        return num2words[num-num%10] + num2words[num%10]

client.run(TOKEN)
