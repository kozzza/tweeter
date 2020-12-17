from discord.ext import commands

from decouple import config

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

if __name__ == '__main__':
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			bot.load_extension(f'cogs.{filename[:-3]}')
	
	bot.run(config('DISCORD_BOT_TOKEN'))
