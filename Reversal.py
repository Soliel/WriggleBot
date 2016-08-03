import discord
from discord.ext import commands

class Reversal():
	def __init__(self, bot):
		self.bot = bot
	
	
	@commands.command()
	async def rev(self, *strrev : str):
		
		# Allows the function to take multiple words, because they are seen as seperate arguments.
		revstr = str.join(" ", strrev)
		messlist = []
		a = len(revstr) - 1
		
		for letter in revstr:
			list.append(messlist, revstr[a])
			a -= 1
		revmess = str.join("", messlist)
		await self.bot.say(revmess)
	
	@commands.command(pass_context = True)
	async def ustest(self, ctx, arg : str):
		print(ctx.message.author.id)
		print(arg.strip('<@>'))
		await self.bot.say("<@{}>, {}".format(ctx.message.author.id, arg))
		

def setup(bot):
	bot.add_cog(Reversal(bot))