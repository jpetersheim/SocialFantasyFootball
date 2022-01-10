import requests
import json
import os
from datetime import datetime, timedelta
from replit import db

user_api = "https://api.sleeper.app/v1/user/"#<user_id> or <username>

def get_userleagues_api(userid, year):
  #use to get api link for listing all user leagues
  api_tmp = "https://api.sleeper.app/v1/user/"+userid+"/leagues/nfl/"+year
  return api_tmp
  
league_api = "https://api.sleeper.app/v1/league/"#<league_id>, 
#/rosters for roster_id (using owner_id), 
#/users for team name (using user_id),
#/matchup/<week> for matchup using roster_id

players_api = "https://api.sleeper.app/v1/players/nfl"
#call this once a day and only if requested

nfl_state_api = "https://api.sleeper.app/v1/state/nfl"
#can get current week, season inf

def get_json(link):
  #use to pull data from api link
  response = requests.get(link)
  json_data = json.loads(response.text)
  return json_data

def get_id(userid):
  api_tmp = user_api+userid
  json_data = get_json(api_tmp)
  tmp_id = json_data['user_id']
  return tmp_id

def get_name(userid):
  api_tmp = user_api+userid
  json_data = get_json(api_tmp)
  tmp_name = json_data['username']
  return tmp_name

def get_nfl_state():
  tmp_nfl = get_json(nfl_state_api)
  return tmp_nfl

def update_player_list():
  one_day = timedelta(days=+1)
  curr_time = datetime.now()
  if 'last_player_load' not in db.keys():
      db['last_player_load'] = curr_time
  if db['last_player_load']+one_day <= curr_time:
      db['players_list'] = get_json(players_api)
      print("Updated players list from sleeper")
  return
    
def get_player(playerid):
  tmp_player = db['players_list'][playerid]
  player_info_details = ["full_name","team","pos","status","injury_status"]
  tmp_player_info = []
  [tmp_player_info.append(tmp_player[x]) for x in player_info_details] 
  #status = Inactive, Active
  #status = IR, Out, null
  print(tmp_player_info)
  return tmp_player_info

def get_userleagues(userid, season):
  tmp_leagues = get_json(get_userleagues_api(userid, season))
  user_leagueids = []
  user_leaguenames = []
  user_teamnames = []
  user_leaguestatus = []
  for x in tmp_leagues:
      [user_leagueids.append(x["league_id"])]
      [user_leaguenames.append(x["name"])]
      [user_leaguestatus.append(x['status'])]
  for x in user_leagueids:
      tmp_leagueinfo = get_json(league_api+x+"/users")
      for y in tmp_leagueinfo:
          if y['user_id']==userid:
            if 'team_name' not in y['metadata'].keys():
              [user_teamnames.append("N/A")]
            else:
              [user_teamnames.append(y['metadata']['team_name'])]
  user_leagues = [user_leagueids,user_leaguenames,user_teamnames,user_leaguestatus]
  return user_leagues

def get_team_info(userid, leagueid):
  tmp_teams = get_json(league_api+leagueid+"/rosters")
  for x in tmp_teams:
      if x['owner_id']==userid:
          tmp_team = x
  #team_settings = ['wins','ties','losses','fpts','fpts_against']
  #team_info = ['roster_id','starters','players']
  #tmp_team_info = []
  #[tmp_team_info.append(tmp_team['settings'][x]) for x in team_settings]
  #[tmp_team_info.append(tmp_team[x] for x in team_info)]
  #print(tmp_team_info)
  return(tmp_team)

def get_roster_id(userid, leagueid):
  tmp_teams = get_json(league_api+leagueid+"/rosters")
  for ind, x in enumerate(tmp_teams):
      if x['owner_id']==userid:
          roster_id = ind
  return(roster_id)

def get_matchup(rosterid, leagueid, weeknum):
  tmp_matchups = get_json(league_api+leagueid+"/matchup/"+weeknum)
  for x in tmp_matchups:
      if x['roster_id']==rosterid:
          tmp_matchup = tmp_matchups[x]
          matchupid = x['matchup_id']
  for x in tmp_matchups:
      if x['matchup_id'] == matchupid and x['roster_id'] != rosterid:
          tmp_matchup_opp = tmp_matchups[x]
  tmp_matchup_data = [tmp_matchup,tmp_matchup_opp]
  return tmp_matchup_data
  
    
            
    


          