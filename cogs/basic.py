from discord.ext import commands
import discord

from manager import Manager
from sql_query import SQLQuery, initialize_connection

class Basic(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.manager = Manager()

	@commands.command(name='ping')
	async def ping_command(self, ctx):
		channel = ctx.channel
		await channel.send(f'> Pong :ping_pong:  |  {round(self.bot.latency, 3)} ms')

	@commands.command(name='help')
	async def help_command(self, ctx):
		channel = ctx.channel

		help_field_names = ['!help', '!ping', '!stream', '!subscribe']
		help_field_values = ['Shows this message (general)', 'Returns the latency of the bot (general)',
		'Sets the channel to stream tweets to', 'Subscribes to a twitter user and filters their tweets based on keywords']

		embed = self.manager.create_embed('Help', 'Tweeter posts tweets in a designated Discord channel based on matching criteria.',
		0x36cdff, f'attachment://help_thumbnail.png', help_field_names, help_field_values)
		await channel.send(embed=embed)

def setup(bot):
	bot.add_cog(Basic(bot))