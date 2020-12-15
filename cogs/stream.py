from discord.ext import commands

class Stream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='subscribe')
    def subscribe(self, ctx):
        print(ctx)

    def tweet(self):
        print('test')

def setup(bot):
	bot.add_cog(Stream(bot))