import discord
import sqlite3
import time
from discord.ext import commands

class PetSys():
	
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context = True)
	async def adopt(self, ctx, arg : str ):
		conn = sqlite3.connect('Regul.db')
		cur = conn.cursor()
		owned = False
		cur.execute("SELECT owner, pet FROM PetTable")
		
		for row in cur.fetchall():
			if row[0] == ctx.message.author.id and row[1] == arg:
				owned = True

		if owned == True:
			await self.bot.say("<@{}>, you cannot adopt the same person more than once.".format(ctx.message.author.id))
			cur.close()
			conn.close()
			return
			
		else:
			cur.execute("INSERT INTO PetTable VALUES(?, ?, ?)", (time.time(), ctx.message.author.id, arg))
			conn.commit()
			cur.close()
			conn.close()
			await self.bot.say("<@{}> has adopted {}".format(ctx.message.author.id, arg))
			
	@commands.command(pass_context=True)
	async def pets(self, ctx):
		conn = sqlite3.connect('Regul.db')
		cur = conn.cursor()
		cur.execute("SELECT owner, pet FROM PetTable")
		haspets = False;
		petstr = []
		for row in cur.fetchall():
			if row[0] == ctx.message.author.id:
				petstr.append(row[1])
				haspets = True
		if haspets == False:
			await self.bot.say("<@{}>, you do not have any pets.".format(ctx.message.author.id))
			return
		else:
			await self.bot.say("<@{}>'s Pets are: \n{}".format(ctx.message.author.id, str.join("\n", petstr)))
			
	@commands.command(pass_context=True)
	async def abandon(self, ctx, arg:str):
		conn = sqlite3.connect('Regul.db')
		cur = conn.cursor()
		cur.execute("SELECT owner, pet FROM PetTable")
		for row in cur.fetchall():
			if row[0] == ctx.message.author.id and row[1] == arg:
				cur.execute("DELETE FROM PetTable WHERE owner = ? AND pet = ?",(ctx.message.author.id, arg))
				conn.commit()
				await self.bot.say("<@{}>, has kicked {} out on the streets. In the rain. Like a dick.".format(ctx.message.author.id, arg))
				cur.close()
				conn.close()
				return
		
		await self.bot.say("<@{}>, You don't own {}".format(ctx.message.author.id, arg))
		cur.close()
		conn.close()
				
	
def setup(bot):
	conn = sqlite3.connect('Regul.db')
	cur = conn.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS PetTable(time REAL, owner TEXT, pet TEXT)")
	cur.close()
	conn.close()
	bot.add_cog(PetSys(bot))