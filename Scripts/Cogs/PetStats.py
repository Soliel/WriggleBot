import sqlalchemy
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from Scripts.DataPy.DataObjects import Base, Pet, Owner
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class PetStats():

    def __init__(self, bot):
        self.bot = bot
        self.engine = create_engine('sqlite:///Data\PetInfo.db')
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()

    @commands.command(pass_context=True)
    async def UpdateValues(self, ctx):
        if not ctx.message.author.id == "96013796681736192":
            await self.bot.say("You cannot use this command.")
            return

        for pet in self.session.query(Pet).all():
            pet.AttribPTS = pet.Level
            pet.AttribATKPTS = 0
            pet.AttribDEFPTS = 0
            pet.AttribHPPTS = 0
            pet.AttribLCKPTS = 0
            pet.AttribACCPTS = 0
            pet.AttribEVAPTS = 0
            self.session.commit()

        await self.bot.say("Changes made to Database")

    @commands.command(pass_context=True)
    async def addstat(self, ctx, arg, amount : int):
        stat = arg.upper()
        valid_stats =  ["ATK", "DEF", "HP", "LCK", "ACC", "EVA"]
        if not any(stat in stats for stats in valid_stats):
              await self.bot.say("That is not a valid stat, please use ``wrig statshelp`` for a list of all valid stats and their effects.")
              return  
        try:
            pet = self.session.query(Pet).filter(Pet.PetID == ctx.message.author.id).one()
        except:
            await self.bot.say("You are not a registered pet.")
            return

        if  pet.AttribPTS < amount:
            await self.bot.say("You do not have enough available points for this.")
            return

        if stat == valid_stats[0]:
            pet.AttribATKPTS += amount
            self.session.commit()
        elif stat == valid_stats[1]:
            if pet.AttribDEFPTS + amount > 300:
                await self.bot.say("You cannot put that many points into DEF")
                return
            pet.AttribDEFPTS += amount
            self.session.commit()
        elif stat == valid_stats[2]:
            pet.AttribHPPTS += amount
            self.session.commit()
        elif stat == valid_stats[3]:
            if pet.AttribLCKPTS + amount > 300:
                await self.bot.say("You cannot put that many points into LCK")
                return
            pet.AttribLCKPTS += amount
            self.session.commit()
        elif stat == valid_stats[4]:
            pet.AttribACCPTS += amount
            self.session.commit()
        elif stat == valid_stats[5]:
            pet.AttribEVAPTS += amount
            self.session.commit()

        pet.AttribPTS -= amount
        self.session.commit()
        self.session.close()
        await self.bot.say("Stat points changed.")

    @commands.command()
    async def statshelp(self):
        await self.bot.say("Current stats and scalings:" +
                           "\n```" + 
                           "\nATK: 3.64 damage per point" +
                           "\nDEF: 1% more effective HP per point (Max 300)" + 
                           "\nHP:  10HP per point" + 
                           "\nLCK: .33% more crit chance per point (Max 300)" +
                           "\nACC: .06% more chance to hit per point" +
                           "\nEVA: .075% less chance to be hit per point" +
                           "```")

    @commands.command()
    async def statsheet(self, arg : discord.User):
        try:
            pet = self.session.query(Pet).filter(Pet.PetID == arg.id).one()
        except:
            await self.bot.say("This is not a valid pet.")
	
        try:
            owner = self.session.query(Owner).filter(Owner.OwnerID == arg.id).one()
            self.Olevel = owner.Level
        except:
            self.Olevel = 0

        await self.bot.say("Pet stat sheet:"+
                           "\n```" +
                           "\nName: {}".format(pet.PetFriendlyName) + 
                           "\nLevel: {}".format(pet.Level) + 
                           "\nOwner Level: {}".format(self.Olevel) +
                           "\nAttack Damage:   {0:.2f}   Attack Points:   {1}".format(pet.AttribATK + (3.64*pet.AttribATKPTS), pet.AttribATKPTS) + 
                           "\n% Damage Taken:  {0:.2f}    Defense Points:  {1}".format(100/(100+pet.AttribDEFPTS+pet.AttribDEF), pet.AttribDEFPTS) + 
                           "\nHit Points:      {0}      Health Point:    {1}".format(pet.AttribHP + (10*pet.AttribHPPTS), pet.AttribHPPTS) +
                           "\nCritical Chance: {0:.2f}%   Luck Points:     {1}".format((pet.AttribLCK * 100)+(.33*pet.AttribLCKPTS), pet.AttribLCKPTS) +
                           "\nEvasion Chance:  {0:.2f}%   Evasion Points:  {1}".format((pet.AttribEVA * 100)+(.075*pet.AttribEVAPTS), pet.AttribEVAPTS) +
                           "\nChance to Hit:   {0:.2f}%  Accuracy Points: {1}".format((pet.AttribACC * 100)+(.06*pet.AttribACCPTS), pet.AttribACCPTS) +
                           "\nAvailable points: {0}".format(pet.AttribPTS) + 
                           "```")

    @commands.command(pass_context=True)
    async def remstat(self, ctx, arg, amount : int):
        
        stat = arg.upper()
        valid_stats =  ["ATK", "DEF", "HP", "LCK", "ACC", "EVA"]
        
        if not any(stat in stats for stats in valid_stats):
              await self.bot.say("That is not a valid stat, please use ``wrig statshelp`` for a list of all valid stats and their effects.")
              return  

        try:
            pet = self.session.query(Pet).filter(Pet.PetID == ctx.message.author.id).one()
        except:
            await self.bot.say("You are not a registered pet.")
            return

        if stat == valid_stats[0]:
            if amount > pet.AttribATKPTS:
                await self.bot.say("You cannot remove this many points from ATK")
                return

            pet.AttribATKPTS -= amount
            self.session.commit()

        elif stat == valid_stats[1]:
            if amount > pet.AttribDEFPTS:
                await self.bot.say("You cannot remove this many points from DEF")
                return

            pet.AttribDEFPTS -= amount
            self.session.commit()

        elif stat == valid_stats[2]:
            if amount > pet.AttribHPPTS:
                await self.bot.say("You cannot remove this many points from HP")
                return
            pet.AttribHPPTS -= amount
            self.session.commit()

        elif stat == valid_stats[3]:
            if amount > pet.AttribLCKPTS:
                await self.bot.say("You cannot remove this many points from LCK")
                return

            pet.AttribLCKPTS -= amount
            self.session.commit()

        elif stat == valid_stats[4]:
            if amount > pet.AttribACCPTS:
                await self.bot.say("You cannot remove this many points from ACC")
                return

            pet.AttribACCPTS -= amount
            self.session.commit()

        elif stat == valid_stats[5]:
            if amount > pet.AttribEVAPTS:
                await self.bot.say("You cannot remove this many points from EVA")
                return

            pet.AttribEVAPTS -= amount
            self.session.commit()

        pet.AttribPTS += amount
        self.session.commit()
        self.session.close()
        await self.bot.say("Stat points changed.")

def setup(bot):
    bot.add_cog(PetStats(bot))