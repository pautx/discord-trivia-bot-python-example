#!/usr/bin/python3
import discord
import sqlite3
import random
import asyncio

database = 'example.db'
sqlTriviaTable = 'example_trivia'
triviaTime = 10.0

conn = sqlite3.connect(database)
c = conn.cursor()
c.execute('SELECT * FROM {}'.format(sqlTriviaTable))
triviaTable = c.fetchall()
tableLength = len(triviaTable)
prefix = '!'

helpMessage = '''
Introducing Trivia Bot!
`!help`                          This message
`!trivia`                       Generate a trivia question
'''

class MyClient(discord.Client):
    free = True

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        # Help Command
        if message.content == '{}help'.format(prefix):
            await message.channel.send(helpMessage)

        # Trivia Command
        if message.content == '{}trivia'.format(prefix) and self.free:
            self.free = False
            triviaID = random.randrange(0, tableLength)
            answer = triviaTable[triviaID][2]
            
            # Ask question
            await message.channel.send(triviaTable[triviaID][1])

            # Check if any user reply is correct
            def isCorrect(reply):
                return reply.content.lower() == answer.lower()
            
            # Check channel chat for correct answer before time runs out    
            try:
                attempt = await self.wait_for('message', check=isCorrect, timeout=triviaTime)
            except asyncio.TimeoutError:
                self.free = True
                return await message.channel.send('Time\'s up! The answer is **{}**.'.format(answer))
            
            # if answer is correct
            if attempt.content.lower().strip() == answer.lower():
                self.free = True
                await message.channel.send('**{}** is correct! Good job {}!'.format(answer, str(attempt.author)[:-5]))

MyClient().run('token')

