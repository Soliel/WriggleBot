import discord
from discord.ext import commands

class Meme():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wes(self):
        await self.bot.say("http://i.imgur.com/9E9jPJa.jpg")

def setup(bot):
    bot.add_cog(Meme(bot))