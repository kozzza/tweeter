from discord.ext import commands
from discord_webhook import DiscordWebhook
import discord

from sql_query import SQLQuery
from sql_query import initialize_connection

from twitter_api import Streamer

import asyncio
import re
import time

class Stream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sql_query = SQLQuery(initialize_connection())
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user}')
        tasks = self.sql_query.select_data('keywords', ['*'])
        tasks = self.sql_query.raw_query(
            '''
            SELECT keywords.user_id, keywords.account, keywords.keywords, guilds.webhook_url
            FROM keywords
            LEFT JOIN guilds
            ON keywords.guild_id = guilds.guild_id;
            ''')
        for task in tasks:
            stream = Streamer(task[3], [task[0]])
            stream.set_filter([task[1]] if task[1] else None, task[2].split(',') if task[2] else None)
            
        await self.bot.change_presence(activity=discord.Game(name=f"!help | {len(tasks)} tasks running"))

    @commands.command(name='stream')
    async def stream_command(self, ctx):
        author = ctx.author
        channel = ctx.channel

        async def set_stream():
            await channel.send('Enter the webhook url of the channel you would like to set streams to')
            webhook_url = ['']

            def check(m):
                if m.author == author and m.channel == channel:
                    test_webhook = DiscordWebhook(url=m.content, content='Testing... 1-2-3. Looks like it works :)')        
                    tweet_response = test_webhook.execute()
                    webhook_url[0] = m.content
                    return True
                else:
                    return False
            try:
                user_confirmation = await self.bot.wait_for('message', check=check)
            except Exception as e:
                await channel.send('Invalid webhook url, try again')
                await set_stream()

            return webhook_url[0]

        webhook_url = await set_stream()
        self.sql_query.insert_and_update('guilds', ['guild_id', 'webhook_url'], [ctx.guild.id, webhook_url], ['guild_id'])
        await channel.send('Successfully set stream :thumbsup:')

    @commands.command(name='subscribe')
    async def subscribe_command(self, ctx):
        author = ctx.author
        channel = ctx.channel

        webhook_url = self.sql_query.select_data('guilds', ['webhook_url'], condition=[['guild_id'], [ctx.guild.id]])
        if not webhook_url:
            await channel.send("Stream has not been set for guild (see !help)")
            return

        stream = Streamer(webhook_url[0][0], [author.id])
        params = {'account':[], 'keywords':[]}

        async def account_verifier(params):
            await channel.send('Enter account username or link to subscribe to (or - to skip)')

            def check(m):
                username = m.content.replace('https://twitter.com/', '') if m.content.startswith('https') else m.content
                if m.author == author and m.channel == channel and (stream.get_user_id(username) or username == '-'):
                    params['account'] = None if username == '-' else username
                    return True
                elif m.author == author and m.channel == channel:
                    raise Exception
                else:
                    return False
            try:
                user_confirmation = await self.bot.wait_for('message', check=check)
            except Exception as e:
                await channel.send('Could not find that user, try again')
                await account_verifier(params)

        async def keyword_verifier(params):
            await channel.send('Enter keywords to detect separated by commas or spaces (or + for all tweets)')

            def check(m):
                if m.author == author and m.channel == channel and not params['account'] and m.content == '+':
                    raise Exception
                elif m.author == author and m.channel == channel:
                    params['keywords'] = None if m.content == '+' else ' '.join(list(filter(None, re.split(',|, | ', m.content))))
                    return True
                else:
                    return False
            try:
                user_confirmation = await self.bot.wait_for('message', check=check)
            except Exception as e:
                await channel.send('You must specify keywords if an account is not specified')
                await keyword_verifier(params)

        await account_verifier(params)
        await keyword_verifier(params)
        acc, keys = params['account'], params['keywords']

        self.sql_query.insert_and_update('keywords', ['guild_id', 'user_id', 'account', 'keywords'], [ctx.guild.id, ctx.author.id, acc if acc else None, keys if keys else None], [])

        stream.set_filter([acc] if acc else None, [keys] if keys else None)
        await channel.send(f'Now monitoring tweets {("from @"+acc+" ") if acc else ""}{("for +"+" +".join(keys.split(" "))+" ") if keys else ""}:thumbsup:')

def setup(bot):
	bot.add_cog(Stream(bot))