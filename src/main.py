# -*- coding: utf-8 -*-
#!/usr/bin/python

from discord import channel, message, user
import discord.ext
from discord.ext import commands, tasks

from test import *
import threading
import time
import logging
from timetableMod import *

from discord_buttons_plugin import *

client = commands.Bot(command_prefix='?')
buttons = ButtonsClient(client)

global timetable_channel
global t
global current_user_button
global valid_channel_cmd
global roles_available

timetable_channel = None
current_user_button = None
roles_available = []
t=0
roles_time_table = ['[1H, HH, QH, LW]', '[HH, QH, LW]', '[QH, LW]', '[LW]', '[NO_NOTIF]']
valid_channel_cmd = None

thumbnail_url = 'link goes here'
image_url = 'link goes here'
ics_author = 'The University/Organisation(web-site.domain)'
icon_url = 'link goes here'

DEBUG_2 = False

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
    EVENTS FOR THE BOT
"""
@client.event
async def on_ready():

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----------')
    # status
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('What is your next class v1.0.0'))
    #make bot reply only into timetablerdr channel. If it doesn't exist, exit--------------------
    global valid_channel_cmd
    valid_channel_cmd = None
    valid_bot_cmd_found = True

    available_channels = client.guilds[0].channels
    valid_bot_reply_channel = 'timetablerdr'

    for i in range(len(available_channels)):
        if str(available_channels[i]) == valid_bot_reply_channel:
            # then send the message there
            valid_channel_cmd = available_channels[i]
            valid_bot_cmd_found = True
            break
    
    if valid_bot_cmd_found:
        print(f'Valid channel: {valid_bot_reply_channel} to reply found')
    else:
        valid_channel_cmd = None
        print(f'Valid channel: {valid_bot_reply_channel} to reply not found')

    #make bot reply only into timetablerdr channel. If it doesn't exist, exit---------------------

    notifier.start()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('What did you say to me?')

# EVENTS ENDS HERE
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------








#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
    COMMANDS FOR THE BOT
"""
# BASICS
@client.command()
async def ping(ctx):
    global valid_channel_cmd
    #print(f'Valid_channel: {valid_channel_cmd}, current channel: {ctx.channel}')

    if valid_channel_cmd == ctx.channel:
        await ctx.send(f'uh oh, CHILL. I am not sleeping. [{round(client.latency*1000)} ms]')

@client.command()
async def hey(ctx):
    global valid_channel_cmd
    if valid_channel_cmd == ctx.channel:
        await ctx.send(f'Hello :) !')

@client.command()
async def tired(ctx):
    global valid_channel_cmd
    if valid_channel_cmd == ctx.channel:
        await ctx.send(f'Sounds like a YOU problem >_>')

@client.command()
async def sup(ctx):
    global valid_channel_cmd
    
    if valid_channel_cmd == ctx.channel:
        global current_user_button

        embed = discord.Embed(
            title = 'TimeTableRdr, a Sentient bot :p ',
            description = 'Hi, Nothing special, you good?',
            color = discord.Color.blue()
        )

        current_user_button = ctx.message.author
        embed.set_footer(text=f'Current_user {current_user_button}')
        
        await buttons.send(
            content = None,
            embed = embed,
            channel = ctx.channel.id,
            components = [
                ActionRow([
                    Button(
                        label = 'Yee',
                        style = ButtonType().Success,
                        custom_id = 'button_yee'
                    ),
                    Button(
                        label = 'Kinda',
                        style = ButtonType().Secondary,
                        custom_id = 'button_kinda'
                    ),
                    Button(
                        label = 'Nope',
                        style = ButtonType().Primary,
                        custom_id = 'button_nope'
                    )
                ])
            ]
        )

@client.command(aliases=['Nice', 'OI'])
async def nice(ctx):
    global valid_channel_cmd
    if valid_channel_cmd == ctx.channel:
        await ctx.send('This one is better: {0:.9f}'.format(13883/33))




# NOTIF
@client.command()
async def nextclass(ctx):
    global valid_channel_cmd
    if valid_channel_cmd == ctx.channel:

        next_class = intro_next_cls()
        #next_class.introduce()

        title       = next_class.getTitle()
        start_time  = next_class.getBegin()
        end_time    = next_class.getEnd()
        descp       = next_class.getDesc()
        latest_mod  = next_class.getLates_mod()
        location    = next_class.getLocation()
        internet    = next_class.getInternet()
        uid         = next_class.getUID()

        embed = discord.Embed(
            title = title,
            description = descp,
            color = discord.Color.blue()
        )

        embed.set_footer(text=f'Retrieved from internet time: {internet}. UID: {uid} ^_^')
        
        # Maybe set some specific images regarding the class
        embed.set_image(url=image_url)
        embed.set_thumbnail(url=thumbnail_url)
        embed.set_author(name=ics_author, icon_url=icon_url)
        
        embed.add_field(name='START TIME', value=start_time, inline=False)
        embed.add_field(name='END TIME', value=end_time, inline=True)
        embed.add_field(name='Latest mod. time', value=latest_mod, inline=True)

        embed.add_field(name='WHERE', value=location, inline=True)
        
        await ctx.send(embed=embed)

@client.command()
async def mynotif(ctx):
    global valid_channel_cmd
    if valid_channel_cmd == ctx.channel:
        global current_user_button
        embed = discord.Embed(
            title = 'TimeTableRdr notifications control',
            description = 'Select your notifications preferences.\n\nDuration before\n1H : 1 hours; HH : Half hour; QH : 15 mins; LW: 5mins.\n\n000 -> No Notif\n001  -> [LW]\n010  -> [QH, LW]\n011   -> [HH, QH, LW]\n100  -> All [1H, HH, QH, LW]',
            color = discord.Color.blue()
        )

        current_user_button = ctx.message.author
        embed.set_footer(text=f'Current_user {current_user_button}')

        # the buttons
        await buttons.send(
            content = None,
            embed = embed,
            channel = ctx.channel.id,
            components = [
                ActionRow([
                    Button(
                        label = '100',
                        style = ButtonType().Success,
                        custom_id = 'button_all_notif'
                    ),
                    Button(
                        label = '011',
                        style = ButtonType().Secondary,
                        custom_id = 'button_notif_v2'
                    ),
                    Button(
                        label = '010',
                        style = ButtonType().Primary,
                        custom_id = 'button_notif_v3'
                    ),
                    Button(
                        label = '001',
                        style = ButtonType().Danger,
                        custom_id = 'button_notif_v4'
                    ),
                    Button(
                        label = '000',
                        style = ButtonType().Secondary,
                        custom_id = 'button_no'
                    )
                ])
            ]
        )


#GET AVAILABLE ROLES
@client.command()
async def roles(ctx):
    global roles_available
    global valid_channel_cmd
    
    if valid_channel_cmd == ctx.channel:
        for role_id in ctx.guild.roles:
            roles_available.append(role_id)

        roles_name = []
        for i in range(len(roles_available)):
            roles_name.append(roles_available[i].name)
        
        await ctx.send(f'Roles names: {roles_name}')

@client.command()
async def setnotifchannel(ctx):
    global valid_channel_cmd
    if valid_channel_cmd == ctx.channel:
        global timetable_channel

        timetable_channel = ctx.channel
        print(timetable_channel)
        await ctx.send('Got it, current channel == notification channel')

@client.command()
async def display(ctx):
    global valid_channel_cmd
    if valid_channel_cmd == ctx.channel:
        embed = discord.Embed(
            title = 'Title',
            description = 'This is a description',
            color = discord.Color.blue()
        )

        embed.set_footer(text='This is the footer.')
        embed.set_image(url=image_url)
        embed.set_thumbnail(url=thumbnail_url)
        embed.set_author(name=ics_author, icon_url=icon_url)
        
        embed.add_field(name='Field Name', value='Field Value', inline=False)
        embed.add_field(name='Field Name', value='Field Value', inline=True)
        embed.add_field(name='Field Name', value='Field Value', inline=True)

        await ctx.send(embed=embed)

# COMMANDS ENDS HERE
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------







#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
    BUTTONS HANDLERS FOR THE BOT
"""
#--- esther start
@buttons.click
async def button_yee(ctx):
    global current_user_button

    if current_user_button == ctx.member:
        await ctx.reply(f'NICE keep it up x) {current_user_button.mention} ^^')
        current_user_button = None

@buttons.click
async def button_kinda(ctx):
    global current_user_button

    if current_user_button == ctx.member:
        await ctx.reply(f'Well, me neither. Hang in there {current_user_button.mention}!')
        current_user_button = None

@buttons.click
async def button_nope(ctx):
    global current_user_button

    if current_user_button == ctx.member:
        await ctx.reply(f'{current_user_button.mention} uh oh ?!')
        current_user_button = None

@buttons.click
async def button_no(ctx):
    global current_user_button

    if current_user_button == ctx.member:
        # send another button thing, are you sure?
        embed = discord.Embed(
            title = 'TimeTableRdr notification control',
            description = f'{current_user_button.mention} Are you sure you want to DISABLE all notifications?',
            color = discord.Color.red()
        )
        # the buttons
        await buttons.send(
            content = None,
            embed = embed,
            channel = ctx.channel.id,
            components = [
                ActionRow([
                    Button(
                        label = 'YES',
                        style = ButtonType().Success,
                        custom_id = 'button_no_valid'
                    ),
                    Button(
                        label = 'NO',
                        style = ButtonType().Secondary,
                        custom_id = 'button_no_not_valid'
                    )
                ])
            ]
        )

@buttons.click
async def button_no_valid(ctx):
    global current_user_button
    global roles_available

    # fetch available roles and save it
    for role_id in ctx.guild.roles:
        roles_available.append(role_id)

    current_role_id = 0
    current_role = '[NO_NOTIF]'

    if current_user_button == ctx.member:
        #assign the role rn
        user_roles = current_user_button.roles # this is the user role, not for the whole server

        # get the current role id from role availbale in the server
        for k in range(len(roles_available)):
            if current_role == str(roles_available[k]):
                current_role_id = roles_available[k]#.id #got it
                print('Current role id ' + str(current_role_id))

        # then start removing exsiting time table role and finally add the new selected one
        for i in range(len(user_roles)):
            if str(user_roles[i]) in roles_time_table:
                print('already have a time_table role set. I am going to delete it')
                print(user_roles[i])
                await current_user_button.remove_roles(user_roles[i]) # remove le deja set role 
                print('roles removed')
                await ctx.reply(f'{current_user_button.mention} Your role(s) {user_roles[i]} has(have) been removed. Old one(s) is(are) kept unchanged.')
                # and then add the new one
                await current_user_button.add_roles(current_role_id)
                await ctx.reply(f'{current_user_button.mention} Your new role {current_role} has been set.')

        await ctx.reply(f'{current_user_button.mention} Alright! No notification for you!')
        current_user_button = None

@buttons.click
async def button_no_not_valid(ctx):
    global current_user_button
    if current_user_button == ctx.member:
        await ctx.reply(f'{current_user_button.mention} Alright! Set your notification preferences then. ?mynotif')
        current_user_button = None

@buttons.click
async def button_all_notif(ctx):
    global current_user_button
    global roles_available
    
    # fetch available roles and save it
    for role_id in ctx.guild.roles:
        roles_available.append(role_id)
    
    current_role = '[1H, HH, QH, LW]'
    current_role_id = 0

    if current_user_button == ctx.member:
        #assign the role rn
        user_roles = current_user_button.roles # this is the user role, not for the whole server

        # get the current role id from role availbale in the server
        for k in range(len(roles_available)):
            if current_role == str(roles_available[k]):
                current_role_id = roles_available[k]#.id #got it
                print('Current role id ' + str(current_role_id))

        # then start removing exsiting time table role and finally add the new selected one
        for i in range(len(user_roles)):
            if str(user_roles[i]) in roles_time_table:
                print('already have a time_table role set. I am going to delete it')
                print(user_roles[i])
                await current_user_button.remove_roles(user_roles[i]) # remove the deja set role 
                print('roles removed')
                await ctx.reply(f'{current_user_button.mention} Your role(s) {user_roles[i]} has(have) been removed. I will add a new TimeTable role.')
                # and then add the new one
                await current_user_button.add_roles(current_role_id)
                await ctx.reply(f'{current_user_button.mention} Your new role {current_role} has been set.')

        await ctx.reply(f'{current_user_button.mention} You will get every notification for the classes')
        current_user_button = None

@buttons.click
async def button_notif_v2(ctx):
    global current_user_button
    global roles_available
    
    # fetch available roles and save it
    for role_id in ctx.guild.roles:
        roles_available.append(role_id)

    current_role = '[HH, QH, LW]'
    current_role_id = 0

    if current_user_button == ctx.member:
        #assign the role rn
        user_roles = current_user_button.roles # this is the user role, not for the whole server

        # get the current role id from role availbale in the server
        for k in range(len(roles_available)):
            if current_role == str(roles_available[k]):
                current_role_id = roles_available[k]#.id #got it
                print('Current role id ' + str(current_role_id))

        # then start removing exsiting time table role and finally add the new selected one
        for i in range(len(user_roles)):
            if str(user_roles[i]) in roles_time_table:
                print('already have a time_table role set. I am going to delete it')
                print(user_roles[i])
                await current_user_button.remove_roles(user_roles[i]) # remove the deja set role 
                print('roles removed')
                await ctx.reply(f'{current_user_button.mention} Your role(s) {user_roles[i]} has(have) been removed. I will add a new TimeTable role.')
                # and then add the new one
                await current_user_button.add_roles(current_role_id)
                await ctx.reply(f'{current_user_button.mention} Your new role {current_role} has been set.')


        await ctx.reply(f'{current_user_button.mention} You will be notified HH, QH, LW before classes')
        current_user_button = None

@buttons.click
async def button_notif_v3(ctx):
    global current_user_button
    global roles_available
    
    # fetch available roles and save it
    for role_id in ctx.guild.roles:
        roles_available.append(role_id)

    current_role_id = 0
    current_role = '[QH, LW]'

    if current_user_button == ctx.member:
        #assign the role rn
        user_roles = current_user_button.roles # this is the user role, not for the whole server

        # get the current role id from role availbale in the server
        for k in range(len(roles_available)):
            if current_role == str(roles_available[k]):
                current_role_id = roles_available[k]#.id #got it
                print('Current role id ' + str(current_role_id))

        # then start removing exsiting time table role and finally add the new selected one
        for i in range(len(user_roles)):
            if str(user_roles[i]) in roles_time_table:
                print('already have a time_table role set. I am going to delete it')
                print(user_roles[i])
                await current_user_button.remove_roles(user_roles[i]) # remove the deja set role 
                print('roles removed')
                await ctx.reply(f'{current_user_button.mention} Your role(s) {user_roles[i]} has(have) been removed. I will add a new TimeTable role.')
                # and then add the new one
                await current_user_button.add_roles(current_role_id)
                await ctx.reply(f'{current_user_button.mention} Your new role {current_role} has been set.')

        await ctx.reply(f'{current_user_button.mention} You will be notified QH, LW before classes')
        current_user_button = None

@buttons.click
async def button_notif_v4(ctx):
    global current_user_button
    global roles_available

    # fetch available roles and save it
    for role_id in ctx.guild.roles:
        roles_available.append(role_id)

    current_role_id = 0
    current_role = '[LW]'
    
    
    if current_user_button == ctx.member:
        #assign the role rn
        user_roles = current_user_button.roles # this is the user role, not for the whole server

        # get the current role id from role availbale in the server
        for k in range(len(roles_available)):
            if current_role == str(roles_available[k]):
                current_role_id = roles_available[k]#.id #got it
                print('Current role id ' + str(current_role_id))

        # then start removing exsiting time table role and finally add the new selected one
        for i in range(len(user_roles)):
            if str(user_roles[i]) in roles_time_table:
                print('already have a time_table role set. I am going to delete it')
                print(user_roles[i])
                await current_user_button.remove_roles(user_roles[i]) # remove the deja set role 
                print('roles removed')
                await ctx.reply(f'{current_user_button.mention} Your role(s) {user_roles[i]} has(have) been removed. I will add a new TimeTable role.')
                # and then add the new one
                await current_user_button.add_roles(current_role_id)
                await ctx.reply(f'{current_user_button.mention} Your new role {current_role} has been set.')

        await ctx.reply(f'{current_user_button.mention} You will be notified only 5 mins before. Are you sure? Ok')
        current_user_button = None
# NOTIF
# BUTTONS HANDLERS ENDS HERE
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------








#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
    LOOP FOR THE BOT
"""
@tasks.loop(seconds=1)
async def notifier():
    global my_current_tz
    global roles_time_table
    global t

    server_id = client.guilds
    current_role_to_mention = None

    found_channel = False
    valid_channel_name = 'timetable' # where to send the notifs

    GO = False

    now = time.time()
    if t%(60*5) == 0:   # time tick every 5 mins
        now_human = datetime.fromtimestamp(now).astimezone().strftime("%A %d. %B %Y - %H:%M:%S")
        print(f'UTC: {now_human}\n')
        
        print('Just checking')
    t+=1

    # checking if there's upcomming class
    now = time.time()
    data_rcv = NOTIFY(now)

    if len(data_rcv) == 0:
        if DEBUG_2:
            print('no_data')
    elif data_rcv[0] == True:
        GO = True
        if DEBUG_2:
            print('Ordered to send notification')
            print(f'Data: {data_rcv[1]}.\t {data_rcv[2]}')
    
    if DEBUG_2:
        print(data_rcv)
        print(f'Time now (FAKE) {my_current_tz}')

    if not GO:
        pass
    else:
        # create the whole embed to send the data
        obj_rcv         = data_rcv[1]

        kind_words  = data_rcv[2]
        notif_type = data_rcv[3]

        title       = obj_rcv.getTitle()
        start_time  = obj_rcv.getBegin()
        end_time    = obj_rcv.getEnd()
        descp       = obj_rcv.getDesc()
        #latest_mod  = obj_rcv.getLates_mod()
        location    = obj_rcv.getLocation()
        internet    = obj_rcv.getInternet()
        uid         = obj_rcv.getUID()

        print('server id : ', server_id)
        # client.guilds server id and name
        # I need to know available roles there
        there_roles = client.guilds[0].roles
        there_channels = client.guilds[0].channels

        for i in range(len(there_channels)):
            if str(there_channels[i]) == valid_channel_name:
                # then send the message there
                channel = there_channels[i]
                found_channel = True
            else:
                found_channel = False
                channel = None

        if notif_type == '1H':
            for i in range(len(there_roles)):
                if str(there_roles[i]) in roles_time_table[0]:
                    current_role_to_mention = there_roles[i]
            #print('Mention: ', current_role_to_mention)
            #await channel.send(f'{current_role_to_mention.mention}')
        elif notif_type == 'HH':
            for i in range(len(there_roles)):
                if str(there_roles[i]) in roles_time_table[1]:
                    current_role_to_mention = there_roles[i]
            #print('Mention: ', current_role_to_mention)
            #await channel.send(f'{current_role_to_mention.mention}')
        elif notif_type == '15m':
            for i in range(len(there_roles)):
                if str(there_roles[i]) in roles_time_table[2]:
                    current_role_to_mention = there_roles[i]    
            #print('Mention: ', current_role_to_mention)
            #await channel.send(f'{current_role_to_mention.mention}')
        elif notif_type == '5m':
            for i in range(len(there_roles)):
                if str(there_roles[i]) in roles_time_table[3]:
                    current_role_to_mention = there_roles[i]
            #print('Mention: ', current_role_to_mention)
            #await channel.send(f'{current_role_to_mention.mention}')

        mention_desc = str(f'{current_role_to_mention.mention}\n') + str(descp)

        embed = discord.Embed(
            title = title,
            description = mention_desc,
            color = discord.Color.red()
        )
        embed.set_footer(text=f'Retrieved from internet time: {internet}. UID: {uid} ^_^')
        
        # Maybe set some specific images regarding the class
        embed.set_footer(text='This is the footer.')
        embed.set_image(url=image_url)
        embed.set_thumbnail(url=thumbnail_url)
        embed.set_author(name=ics_author, icon_url=icon_url)

        embed.add_field(name='\nSTART TIME', value=start_time, inline=False)
        embed.add_field(name='END TIME', value=end_time, inline=True)
        #add a field for the kind words (latest mod removed)
        embed.add_field(name='KIND WORDS FOR YOU', value=kind_words, inline=True)
        embed.add_field(name='WHERE', value=location, inline=True)

        # send the notification NOW
        #check before if my required channel aka 'timetable' exist on the server
        #if not, no notif
        if found_channel:
            print(f'Channel {valid_channel_name}: found')
            # already mentionned earlier
            await channel.send(f'{current_role_to_mention.mention}\n') # or I will ping them again. Embed one seems not to work
            await channel.send(embed=embed,)
        else:
            print(f'Missing {valid_channel_name} channel')

        #print('Updated')
        #------------------- D           O               N                 E

# LOOP ENDS HERE
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------









#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
                MAIN                LOOP
"""
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    #logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    #logging.info('  MAIN:         Starting the bot.')

    client.run('your_discord_token')



