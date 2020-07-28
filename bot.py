import os
import random
import ssl

import discord
from discord.ext import commands
from dotenv import load_dotenv
import emoji


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('SERVER_NAME')

num2emojis = {1: 'POGGERS', 2: 'KEKW', 3: '5Head', 4: '3Head', 5: 'Coomer', 6: 'FeelsRainMan', 7: 'HACKERMANS', 8: 'PartyKirby', 9: 'ricardoFlick'}

movie_list = {}
killers = []
movie_nominated = {}
killer_counts = {}

client = commands.Bot(command_prefix='$')

## TODO:
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

    # keep track of how many times every player in the server has been killer
    for member in server.members:
        killer_counts[member.name] = 0
        movie_nominated[member.name] = False


@client.event
async def on_member_join(member):
    killer_counts[member.name] = 0
    movie_nominated[member.name] = False


@client.event
async def on_member_update(before, after):
    # update DbD tracking
    killer_counts[after.name] = killer_counts[before.name]
    del(killer_counts[before.name])

    if before.name in killers:
        killers.append(after.name)
        for killer in killers:
            if killer == before.name:
                del(killer)

    # update Movie Night tracking
    movie_nominated[after.name] = movie_nominated[before.name]
    del(movie_nominated[before.name])

    if before.name in movie_list.keys():
        movie_list[after.name] = movie_list[before.name]
        del(movie_list[before.name])


@client.command(name='nominate')
async def nominate(ctx, movie):
    user = ctx.message.author.name
    if movie_nominated[user]:
        await ctx.send("Sorry! You've already nominated a movie. You can undo your nomination with `$undo`")
        return
    if movie not in movie_list and not movie_nominated[user]:
        movie_list[user] = movie
        movie_nominated[user] = True


@client.command(name='undo')
async def undo(ctx):
    user = ctx.message.author.name
    if not movie_nominated[user]:
        await ctx.send("Hmmm...looks like you haven't nominated a movie!")
        return
    else:
        movie_nominated[user] = False
        del(movie_list[user])


@client.command(name='movies')
async def movies(ctx):
    if len(movie_list) == 0:
        return

    vote_movies = ''
    for movie in movie_list.values():
        vote_movies = vote_movies + f'{movie}\n'

    await ctx.send(vote_movies)


@client.command(name='vote')
async def vote(ctx):
    server = discord.utils.get(client.guilds, name=SERVER)

    poll = '**Movie to Watch:**\n'
    count = 1

    for movie in movie_list.values():
        poll += f'{discord.utils.get(server.emojis, name=num2emojis[count])} - {movie}\n'
        count += 1

    message = await ctx.send(poll)

    for i in range(1, len(movie_list) + 1):
        emoji = discord.utils.get(server.emojis, name=num2emojis[i])
        await message.add_reaction(emoji)


@client.command(name='new')
async def new(ctx):
    movie_list.clear()

    for member in movie_nominated.keys():
        movie_nominated[member] = False


@client.command(name='killer')
async def killer(ctx):
    killer = ctx.message.author.name
    if killer not in killers:
        killers.append(killer)


@client.command(name='choose')
async def choose(ctx):
    if len(killers) == 0:
        await ctx.send("No-one has volunteered for killer. Have someone volunteeer with `$killer` then try again!")
        return

    potential_killers = _find_killers(0)

    killer = potential_killers[random.choice(range(len(potential_killers)))]
    killer_counts[killer] = killer_counts[killer] + 1
    await ctx.send(f'{killer} is the killer!')
    killers.clear()


def _find_killers(kill_count):
    potential_killers = []

    for killer in killers:
        if killer_counts[killer] == kill_count:
            potential_killers.append(killer)

    if len(potential_killers) == 0:
        potential_killers = _find_killers(kill_count + 1)

    return potential_killers


client.run(TOKEN)
