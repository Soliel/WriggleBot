import sqlalchemy
import discord
import random
import decimal
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from Scripts.DataPy.DataObjects import Base, Pet, Owner
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

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
        
        if self.pet.PetID == self.enemy.PetID:
            await self.bot.say("You cannot battle yourself.")
            return False
        elif self.pet.OwnerID == ownerID: 
            return True
        elif self.owner.OwnerID == self.pet.PetID:
            return True
        else:
            await self.bot.say("You don't own this User")
            return False


    @commands.cooldown(1, 15, BucketType.user)
    @commands.command(pass_context = True)
    async def battle(self, ctx, arg : discord.User, arg2 : discord.User):

        print("checking users.")
        if not await self.Get_Battle_Users(ctx.message.author.id, arg.id, arg2.id):
            self.session.close()
            return
		
        if self.pet.Level < self.enemy.Level:
            self.target = self.pet
        else:
            self.target = self.enemy

        print("Beginning battle")
        self.EnemyHP = int(self.enemy.AttribHP) + (10*self.enemy.AttribHPPTS)
        self.PetHP = int(self.pet.AttribHP) + (10*self.pet.AttribHPPTS)
        self.pethit = 0
        self.petmiss = 0
        self.enemyhit = 0
        self.enemymiss = 0
        self.enemyDamage = 0
        self.petDamage = 0
        self.petCrit = 0
        self.enemyCrit = 0

        print("{0} \n {1}".format(self.PetHP, self.EnemyHP))

        while(self.EnemyHP > 0 and self.PetHP > 0):
            print("Fighting!")
            if self.didHit(self.pet, self.enemy):
                self.pethit += 1
                dmg = self.Get_Damage(self.pet, self.enemy)
                if self.didCrit: self.petCrit += 1
                self.EnemyHP -= dmg
                self.petDamage += dmg
            else:
                self.petmiss += 1
            
            if self.EnemyHP <= 0:
                exp = self.calc_experience(self.owner, self.target)
                await self.bot.say("{11}, You have Won!\n\nStats for this battle:"
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
                                   "\nExperience Gained by enemy: {10}```".format(self.pethit, self.petmiss, self.petCrit, int(self.petDamage), self.enemyhit, self.enemymiss, self.enemyCrit, int(self.enemyDamage), int(exp[2]), int(exp[0]), int(exp[1]), ctx.message.author.mention))
                self.pet.Experience += exp[0]
                self.enemy.Experience += exp[1]
                self.owner.Experience += exp[2]
                await self.do_levelups()

                self.session.commit()
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
                exp  = self.calc_experience(self.owner, self.target)
                await self.bot.say("{11}, You have Lost!\n\nStats for this battle:"
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
                                   "\nExperience Gained by enemy: {10}```".format(self.pethit, self.petmiss, self.petCrit, int(self.petDamage), self.enemyhit, self.enemymiss, self.enemyCrit, int(self.enemyDamage), int(exp[2]), int(exp[1]), int(exp[0]), ctx.message.author.mention))
                self.enemy.Experience += exp[0]
                self.pet.Experience += exp[1]
                self.owner.Experience += exp[2]
                await self.do_levelups()
                
                self.session.commit()
                self.session.close()
                return
        
    def Get_Damage(self, attacker, defender):
        crit = decimal.Decimal(random.randrange(100))/100
        if crit <= attacker.AttribLCK + (.0033*attacker.AttribLCKPTS):
            self.didCrit = True
            return ((attacker.AttribATK + (3.64*attacker.AttribATKPTS)) * 2) * (100/(defender.AttribDEF + defender.AttribDEFPTS + 100))
        else:
            self.didCrit = False
            return (attacker.AttribATK+ (3.64*attacker.AttribATKPTS)) * (100/(defender.AttribDEF + defender.AttribDEFPTS + 100))

    def didHit(self, attacker, defender):
        chanceToHit = (attacker.AttribACC+(.0006*attacker.AttribACCPTS)) - (defender.AttribEVA+(.00075*defender.AttribEVAPTS))
        
        if decimal.Decimal(random.randrange(100))/100 <= chanceToHit:
            return True
        else:
            return False

    def calc_experience(self, owner, defender):
        winner_exp = (10 * (defender.Level ** 1.2))/((defender.Level ** .1162) + 1)
        loser_exp = winner_exp/2
        owner_exp = (10 * (owner.Level ** 2))/(.4 * (owner.Level**1.25) + 1)
        return [winner_exp, loser_exp, owner_exp]

    async def do_levelups(self):
        ownerlvlreq = (10 * (self.owner.Level ** 2))
        petlvlreq = (10 * (self.pet.Level ** 1.2))
        enemylvlreq = (10 * (self.enemy.Level ** 1.2))

        if self.owner.Experience >= ownerlvlreq:
            self.owner.Level += 1
            self.owner.Experience -= ownerlvlreq
            await self.bot.say("You have leveled up! You are now level: {}".format(self.owner.Level))

        if self.pet.Experience >= petlvlreq:
            self.pet.Level += 1
            self.pet.Experience -= petlvlreq
            await self.on_pet_levelup(self.pet)
            await self.bot.say("Your pet has leveled up! Pet is now level: {}".format(self.pet.Level))

        if self.enemy.Experience >= enemylvlreq:
            self.enemy.Level += 1
            self.enemy.Experience -= enemylvlreq
            await self.on_pet_levelup(self.enemy)
            await self.bot.say("Enemy pet has leveled up! enemy is now level: {}".format(self.enemy.Level))

    async def on_pet_levelup(self, pet):
        pet.AttribDEF += .25
        pet.AttribATK += 2
        pet.AttribHP += 5
        pet.AttribPTS += 1
        self.session.commit()

def setup(bot):
    bot.add_cog(PetBattle(bot))