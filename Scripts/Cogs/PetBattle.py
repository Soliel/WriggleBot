import sqlalchemy
import discord
import random
import decimal
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from Scripts.DataPy.DataObjects import Base, Pet, Owner
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Scripts.Cogs.PetClaim import sqlalchemy

class PetBattle():
    
    def __init__(self, bot):
        self.bot = bot
        self.engine = create_engine('sqlite:///Data\PetInfo.db')
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()

    async def Get_Battle_Users(self, ownerID : str, petID : str, EnemyID : str):
        try:
            self.owner = self.session.query(Owner).filter(Owner.OwnerID == ownerID).one()
            self.pet = self.session.query(Pet).filter(Pet.PetID == petID).one()
            self.enemy = self.session.query(Pet).filter(Pet.PetID == EnemyID).one()
        except Exception as e:
            print(e)
            self.owner = None
            self.pet = None
            self.enemy = None
            await self.bot.say("One of the users is not registered.")
            return False
        
        if self.pet.OwnerID == ownerID: 
            return True
        else:
            await self.bot.say("You don't own this User")
            return False
    @commands.cooldown(1, 5, BucketType.user)
    @commands.command(pass_context = True)
    async def battle(self, ctx, arg : discord.User, arg2 : discord.User):
        
        if not await self.Get_Battle_Users(ctx.message.author.id, arg.id, arg2.id):
            self.session.close()
            return

        self.EnemyHP = int(self.enemy.AttribHP)
        self.PetHP = int(self.pet.AttribHP)
        self.pethit = 0
        self.petmiss = 0
        self.enemyhit = 0
        self.enemymiss = 0
        self.enemyDamage = 0
        self.petDamage = 0
        self.petCrit = 0
        self.enemyCrit = 0

        while(self.EnemyHP > 0 and self.PetHP > 0):
            if self.didHit(self.pet, self.enemy):
                self.pethit += 1
                dmg = self.Get_Damage(self.pet, self.enemy)
                if self.didCrit: self.petCrit += 1
                self.EnemyHP -= dmg
                self.petDamage += dmg
            else:
                self.petmiss += 1
            
            if self.EnemyHP <= 0:
                await self.bot.say("You have Won!\n\nStats for this battle:"
                                   "```"
                                   "\nNumber of times your pet hit: {0}"
                                   "\nNumber of times your pet missed: {1}"
                                   "\nNumber of times your pet crit: {2}"
                                   "\nDamage done by your pet: {3}"
                                   "\nNumber of times enemy hit: {4}"
                                   "\nNumber of times enemy missed: {5}"
                                   "\nNumber of times enemy Crit: {6}"
                                   "\nDamage done by enemy: {7}"
                                   "\nExperience Gained by you: {8}"
                                   "\nExperience Gained by your pet: {9}"
                                   "\nExperience Gained by enemy: {10}```".format(self.pethit, self.petmiss, self.petCrit, int(self.petDamage), self.enemyhit, self.enemymiss, self.enemyCrit, int(self.enemyDamage), 0, 0, 0))
                self.session.close()
                return
            
            if self.didHit(self.enemy, self.pet):
                self.enemyhit += 1
                dmg = self.Get_Damage(self.enemy, self.pet)
                if self.didCrit: self.enemyCrit += 1
                self.PetHP -= dmg
                self.enemyDamage += dmg
            else:
                self.enemymiss += 1

            if self.PetHP <= 0:
                await self.bot.say("You have Lost!\n\nStats for this battle:"
                                   "```"
                                   "\nNumber of times your pet hit: {0}"
                                   "\nNumber of times your pet missed: {1}"
                                   "\nNumber of times your pet crit: {2}"
                                   "\nDamage done by your pet: {3}"
                                   "\nNumber of times enemy hit: {4}"
                                   "\nNumber of times enemy missed: {5}"
                                   "\nNumber of times enemy Crit: {6}"
                                   "\nDamage done by enemy: {7}"
                                   "\nExperience Gained by you: {8}"
                                   "\nExperience Gained by your pet: {9}"
                                   "\nExperience Gained by enemy: {10}```".format(self.pethit, self.petmiss, self.petCrit, int(self.petDamage), self.enemyhit, self.enemymiss, self.enemyCrit, int(self.enemyDamage), 0, 0, 0))
                
                self.session.close()
                return
        
    def Get_Damage(self, attacker, defender):
        crit = decimal.Decimal(random.randrange(100))/100
        if crit <= attacker.AttribLCK:
            self.didCrit = True
            return (attacker.AttribATK * 2) * (100/(defender.AttribDEF + 100))
        else:
            self.didCrit = False
            return attacker.AttribATK * (100/(defender.AttribDEF + 100))

    def didHit(self, attacker, defender):
        chanceToHit = attacker.AttribACC - defender.AttribEVA
        
        if decimal.Decimal(random.randrange(100))/100 <= chanceToHit:
            return True
        else:
            return False

    # async def calc_experience(self, owner, winner, loser):
        

def setup(bot):
    bot.add_cog(PetBattle(bot))