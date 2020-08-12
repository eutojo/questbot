import requests
import sqlite3
import json
from bs4 import BeautifulSoup

url = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=SkriptKitty'

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

conn = sqlite3.connect('quests.db')

with open('quest_requirements.json') as json_file:
  quest_requirements = json.load(json_file)

c = conn.cursor()
c.execute('SELECT title FROM quests WHERE completed!="1"')
incomplete = c.fetchall()

todo = []

cantdo = []

for quests in incomplete:
  quest_title = quests[0].replace('_', ' ')
  quest_requirement = quest_requirements[quest_title]

  ## no requirements
  if len(quest_requirement) < 1:
    todo.append(quest_title)
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
      todo.append(quest_title)
    else:
      cantdo.append(quest_title)
# Save (commit) the changes

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

print("Can do: " + str(len(todo)) + " quests.")
for quests in todo:
  print(quests)

# print("Can do: " + str(len(cantdo)) + " quests.")
# for quests in cantdo:
#   print(quests)