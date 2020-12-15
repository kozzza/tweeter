import discord

class Manager():
	def __init__(self):
		pass

	def get_channel_by_name(self, guild, channel_name):
		channel = discord.utils.get(guild.text_channels, name=channel_name)
		return channel
	
	def create_embed(self, title, description, color, thumbnail, field_names, field_values):
		embed = discord.Embed(title=title, description=description, color=color)
		embed.set_author(name="KZ", url="http://koza.pro")
		embed.set_thumbnail(url=thumbnail)
		for i in range(len(field_names)):
			embed.add_field(name=field_names[i], value=field_values[i], inline=False)
		return embed