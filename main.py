import discord
import os
import discord.ext
import sleeper_fn as slp
from datetime import datetime, timedelta
import asyncio
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, check
from replit import db

client = discord.Client()
client = commands.Bot(command_prefix = '!sff-')

ff_apps = ["sleeper"]

def setup_user(member : discord.Member, app, user_id, league_id, league_name):
  tmp_key = str(member.id)

  roster_id = slp.get_roster_id(user_id,league_id)
  
  if not any(tmp_key in k for k in db.keys()):
    db[tmp_key]={}
    db[tmp_key]['leagues']={}

  db[tmp_key][app]=user_id
  db[tmp_key]['leagues'][league_id] = {}
  db[tmp_key]['leagues'][league_id]['league_name'] = league_name
  db[tmp_key]['leagues'][league_id]['roster_id'] = roster_id

  time_curr = datetime.now()
  #db[tmp_key]['updated']=time_curr
  print("Database updated with {0}:[{1}:{2}, {3}:[{4}:[{5}:{6}]], {7}:{8}]".format(tmp_key,app,user_id,'leagues',league_id,'roster_id',roster_id,'updated',time_curr))

def remove_user(member: discord.Member):
 print("remove")   
  
@client.event
async def on_ready():
    print("Social Fantasy Football Bot is online!") #will print when the bot is online
    
@client.command(
  help="Simple command so that when you type ping the bot will respond with pong!",
  brief="Bot replies with pong!"
)
async def ping(ctx):
  await ctx.send("pong!")
  print("pong!")

@client.command(
  help="Use this to add your account information (UserID for sleeper, LeagueID for ESPN) for our supported fantasy football leagues: {0}".format(ff_apps),
  brief="Add account information for the user sending the message"
)
async def setup(ctx, member: discord.Member, app, userid):
  if app in ff_apps:
    if app == "sleeper":
      tmp_value = slp.get_id(userid)
    else:
      tmp_value = userid

    nfl_state = slp.get_nfl_state()
    curr_year = nfl_state['season']
    
    user_lg_info = slp.get_userleagues(tmp_value,curr_year)

    if len(user_lg_info[0]) > 1:
      league_list = []
      for i, val in enumerate(user_lg_info[1],1):
        [league_list.append('{0}. {1}'.format(i, val))]
      str_leagues = '\n'.join(league_list)
    
      await ctx.send('Which league would you like to add?')
      await ctx.send(str_leagues)
      def check(m): return m.author==ctx.author and m.channel==ctx.channel
    
      msg = await client.wait_for('message', check=check, timeout=180)
      msg_answer = int(msg.content)
    
      while msg_answer not in [j for j in range(1,(len(user_lg_info[0])+1))]:
        await ctx.send('Not a correct choice.\nWhich league would you like to add?')
        await ctx.send(str_leagues)
    
        msg = await client.wait_for('message', check=check, timeout=180)
        msg_answer = int(msg.content)
      
      league_id = user_lg_info[0][msg_answer-1]
      league_name = user_lg_info[1][msg_answer-1]
    else:
      msg_answer = 1
      league_id = user_lg_info[0][0]
      league_name = user_lg_info[1][0]
    
    setup_user(member, app, tmp_value, league_id, league_name)
    
    await ctx.send("{0} added information for {1} fantasy football app: {2} {3} {4}".format(ctx.author.mention, app, member.mention, userid, league_name))
  else:
    await ctx.send("SFF does not support {0} fantasy football leagues, please try again with one of our supported leagues. See sff-help setup for a list.".format(app))
  return
      
@client.command(
  help="Use this command to remove a user or league from the database. Specify the type of remove with `user` or `league`",
  brief="Remove a user or league from the database."
)
async def remove(ctx, member : discord.Member, type):
  types = ['user','league']
  if not any(type in t for t in types):
    await ctx.send('Please retry and enter an appropriate type to remove, such as `user` or `league`.')
    return
    
  userid = str(member.id)
  print(userid)
  
  if any(userid in k for k in db.keys()):
    if type == 'user':
      del db[userid]
      await ctx.send("Removed the user {0} from database.".format(member.mention))
      
    elif type =='league':
      leagues_info = db[userid]['leagues']
      
      if len(leagues_info) > 1:
        league_names = []
        league_keys = []
        
        for x in leagues_info:
          [league_names.append(leagues_info[x]['league_name'])]
          [league_keys.append(x)]
          
        league_list = []
        
        for i, val in enumerate(league_names,1):
          league_list.append('{0}. {1}'.format(i, val))
          
        str_leagues = '\n'.join(league_list)
      
        await ctx.send('Which league would you like to remove?')
        await ctx.send(str_leagues)
        def check(m): return m.author==ctx.author and m.channel==ctx.channel
      
        msg = await client.wait_for('message', check=check, timeout=180)
        msg_answer = int(msg.content)
      
        while msg_answer not in [j for j in range(1,(len(league_list)+1))]:
          await ctx.send('Not a correct choice.\nWhich league would you like to remove?')
          await ctx.send(str_leagues)
      
          msg = await client.wait_for('message', check=check, timeout=180)
          msg_answer = int(msg.content)
          
      else:
        league_keys = []
        for x in leagues_info:
          [league_keys.append(x)]
        msg_answer = 1
        
      del_league_name = db[userid]['leagues'][league_keys[msg_answer-1]]['league_name']

      del db[userid]['leagues'][league_keys[msg_answer-1]]
      await ctx.send("Removed the league {0} from user {1}.".format(del_league_name,member.mention))
      
  else:
    await ctx.send("Can't find any leagues setup for {0}. Let them know to set up their fantasy football leagues using the setup command!".format(member.mention))
  return

@client.command(
  help="Use this to check whether a member has set up their fantasy football information",
  brief="Check whether a user has set up fantasy football information."
)
async def checkuser(ctx, member : discord.Member):
  if not any(str(member.id) in k for k in db.keys()):
    await ctx.send("Can't find any leagues setup for {0}. Let them know to set up their fantasy football leagues using the setup command!".format(member.mention))
  else:
    tmp_str = db[str(member.id)]
    await ctx.send(tmp_str)
  return

client.run(os.environ["TOKEN"]) #get your bot token and create a key named `TOKEN` to the secrets panel then paste your bot token as the value. 
#to keep your bot from shutting down use https://uptimerobot.com then create a https:// monitor and put the link to the website that appewars when you run this repl in the monitor and it will keep your bot alive by pinging the flask server
#enjoy!