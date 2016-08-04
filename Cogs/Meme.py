import discord
from discord.ext import commands

class Meme():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wes(self):
        self.bot.say("https://discordcdn.com/attachments/180131069960519680/210620976814227456/Take_me_to_flavour_town.jpg")

def setup(bot):
    bot.add_cog(Meme(bot))