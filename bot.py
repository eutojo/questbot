import discord
import os
import sqlite3
import json
import requests
from random import randrange
from dotenv import load_dotenv

def init(username):
  conn = sqlite3.connect('questbot.db')
  c = conn.cursor()

  ## quest table
  c.execute('''
  CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_name text NOT NULL,
    completed INTEGER,
    UNIQUE(quest_name)
  )''')

  with open('quest_requirements.json') as json_file:
    quest_requirements = json.load(json_file)

    for quests in quest_requirements:
      quests = quests.upper()
      c.execute(('''
      INSERT OR IGNORE INTO quests (quest_name)
      VALUES ("{0}")
      ''').format(quests))
         
  conn.commit()
  #close the connection
  conn.close()

  print('Gathering data for ' + username)
  url = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=' + username

  data = requests.get(url).text.split(',')
  data = data[3:]

  index = 0

  while index < len(data):
    if '\n' in data[index]:
      data.remove(data[index])
      index = 0
    else:
      index += 1

  skill_name = ['Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer', 'Magic', 'Cooking', 'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing', 'Mining', 'Herblore', 'Agility', 'Thieving', 
  'Slayer', 'Farming', 'Runecrafting', 'Hunter', 'Construction']
  skills = {}

  index = 0

  while index < len(data):
    skills[skill_name[index]] = data[index]
    index += 1
  
  with open("player.json", "w") as data:
        player = json.dump(skills, data, indent=4)

def display(display):
  conn = sqlite3.connect('questbot.db')
  c = conn.cursor()
  msg = ''
  if display == 0:
    msg = 'Displaying Completed Quests\n'
    c.execute('''
      SELECT quest_name FROM quests WHERE completed IS NOT NULL
    ''')
  else:
    msg = 'Displaying Incomplete Quests\n'
    c.execute('''
      SELECT quest_name FROM quests WHERE completed IS NULL
    ''')

  res = c.fetchall()

  # Displaying done and not done
  if display < 2:
    res = [x[0] for x in res]
  else:

    todo = []
    cantdo = []

    with open('quest_requirements.json') as json_file:
      quest_requirements = json.load(json_file)
      with open('player.json') as json_file:
        skills = json.load(json_file)
        for quests in res:
          quests = quests[0]
          quest_requirement = quest_requirements[quests]

          if len(quest_requirement) < 1:
            todo.append(quests)
          else:
            can = 0
            for req in quest_requirement:
              req_level = quest_requirement[req]
              cur_level = skills[req]
              if '+' in req_level:
                req_level = req_level[:-1]
              if int(cur_level) >= int(req_level):
                can += 1
            if can == len(quest_requirement):
              todo.append(quests)
            else:
              cantdo.append(quests)

    ## can do
    if display == 2:
      res = todo
    elif display == 3:
      res = cantdo
    else:
      index = randrange(len(todo)-1)
      res = [todo[index]]

  msg += 'Count: ' + str(len(res)) + '\n'
  quests = ''

  for index, items in enumerate(res):
    quests = quests + items + '\n'
    if len(quests) > 1000:
      msg += quests
      msg += '...'
      break
    elif index + 1 == len(res):
      msg += quests

  msg = msg[:-1]  

  conn.close()
  return msg

def update(quest_name, flag):
  conn = sqlite3.connect('questbot.db')
  c = conn.cursor()

  if flag == 0:
    c.execute('''
    UPDATE quests
    SET completed IS NULL
    WHERE
    quest_name = "%s"
    ''' % quest_name)
  else:
    c.execute('''
    UPDATE quests
    SET completed = 1
    WHERE
    quest_name = "%s"
    ''' % quest_name)

  print('Updating: ' + quest_name)

  conn.commit()
  conn.close()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    args = message.content.split(' ')
    command = args[0]

    # bot command detected
    if command == '/qb':
      command = args[1]
      if command == 'init':
        init(args[2])
        msg = 'Bot initialised.'
      # complete
      elif command == '-o':
        msg = display(0)
      # incomplete
      elif command == '-i':
        msg = display(1)
      # can do
      elif command == '-l':
        msg = display(2)
      # cant do
      elif command == '-x':
        msg = display(3)
      # random one to do now
      elif command == '-n':
        msg = display(4)
      # set to complete
      elif command == '-u':
        del args[0]
        del args[0]
        flag = args[len(args)-1]
        del args[len(args)-1]
        quest_name = ' '.join(args).upper()
        update(quest_name, int(flag))
        msg = 'Updated ' + quest_name
      # help
      elif command == '-h':
        msg = '-o : complete\n'
        msg += '-i : incomplete\n'
        msg += '-l : can do\n'
        msg += '-x : cant do\n'
        msg += '-n : do now\n'
        msg += '-u --flag: update status\n'
      else:
        msg = 'I don\'t understand?'
      
      msg = msg.format(message)
      await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)