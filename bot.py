import discord
import os
import sqlite3
from dotenv import load_dotenv

def init:
  conn = sqlite3.connect('questbot.db')
  c = conn.cursor()

  ## user table
  c.execute('''
  CREATE TABLE IF NOT EXISTS user (
    id INTEGER AUTOINCREMENT,
    username text NOT NULL,
  )''')

  c.execute('''
  CREATE TABLE IF NOT EXISTS quests (
    quest_name text NOT NULL,
    completed INTEGER,
  )''')
  
        
  #commit the changes to db			
  conn.commit()
  #close the connection
  conn.close()


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

print(TOKEN)

client = discord.Client()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    args = message.content.split(' ')
    command = args[0]
    

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)