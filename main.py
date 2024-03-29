import discord
import time
import asyncio
import random

client = discord.Client()
roles = {}
nicknames = {}
kickmessages = ["Hasta la vista, {kickeduser:s}!", "{kickeduser:s} was the weakest link. Goodbye.",
                "Looks like you're going to the shadow realm, {kickeduser:s}."] #This list can be added to if more vote to kick messages are desired.

@client.event
async def on_ready():
    print("Logged in\n") #Confirmation of initialization of the bot.

@client.event
async def on_member_join(member): 
    if member in roles: #If the user was previously kicked, this reassigns their previous roles from a dict compiled upon kick.
        for role in roles[member][1:]:
            await member.add_roles(role)
    if member in nicknames: #If the user was previously kicked and had a nickname, this reassigns their previous nickname using a dict compiled upon kick.
        await member.edit(nick=nicknames[member])

@client.event
async def on_message(message): #Checks messages to send and determines if it follows the appropriate format of a vote to kick command.
    if message.content.split(" ")[0] == "!vtk":
        await voteToKick(message)


def check(reaction, user): #Makes sure the reaction type was correct and that the person reacting was neither the person who initiated the kick nor the target of the kick.
    return (user != message.author and user != mention[0] and str(reaction.emoji) == '👞')

async def voteToKick(message):
    mention = message.mentions #Gathers the target of the vote to kick.
    if mention[0].id == 729396157859627079: #Prevents users from kicking the bot.
        botmessage = "I'm sorry, {kicker:s}, I'm afraid I can't do that."
        await message.channel.send(botmessage.format(kicker=("<@" + str(message.author.id) + ">")))
    elif len(mention) != 1: #Prevents multiple people from being kicked.
        return
    else:
        userToKick = mention[0] 
        votedlist = []
        votes = 1
        botMessage = await message.channel.send("Vote to Kick Initiated: 1/4")
        await botMessage.add_reaction('👞')
        endtime = time.time() + (60 * 5)
        while votes < 4:

            try:
                reaction, user = await client.wait_for('reaction_add', timeout = endtime - time.time())
                if (user != message.author and user != userToKick and str(reaction.emoji) == '👞' and user not in votedlist):
                    votes += 1
                    editedmessage = "Vote to Kick Initiated: {votes:d}/4"
                    await botMessage.edit(content=editedmessage.format(votes=votes))
                    votedlist.append(user)
                    continue
                else:
                    await botMessage.remove_reaction(reaction, user)
                    continue
            except asyncio.TimeoutError:
                timeoutMsg = "This vote to kick has timed out."
                await botMessage.edit(content=timeoutMsg)
                break


        if votes >= 4:
            kickedRoles = userToKick.roles
            roles[userToKick] = kickedRoles
            nicknames[userToKick] = userToKick.display_name
            invite = await message.channel.create_invite(max_uses=1,unique=True)
            try:
                await userToKick.send(invite)
                kickmessage = kickmessages[random.randint(0, len(kickmessages) - 1)].format(kickeduser=("<@" + str(userToKick.id) + ">"))
                await message.channel.send(kickmessage)
            except:
                print("error sending message")

            await userToKick.kick()



client.run() #You must put a bot API key from discord here
