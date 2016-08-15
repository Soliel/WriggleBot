import discord
import sqlalchemy
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from Scripts.DataPy.DataObjects import Base, Pet, Owner
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Scripts.Cogs.PetClaim import sqlalchemy

class PetClaim():

    def __init__(self, bot):
        self.bot = bot
        self.engine = create_engine('sqlite:///Data\PetInfo.db')
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()
    
    adoptions = {}
    
    @commands.cooldown(1, 30, BucketType.user)
    @commands.group(pass_context=True, invoke_without_command=True)
    async def adopt(self, ctx, arg : discord.User):
        try:
            owner = self.session.query(Owner).filter(Owner.OwnerID == ctx.message.author.id).one()
        except:
            owner = None

        try:
            pet = self.session.query(Pet).filter(Pet.PetID == arg.id).one()
        except:
            pet = None

        if arg.id == ctx.message.author.id:
            await self.bot.say("You cannot adopt yourself!")
            return

        elif hasattr(pet, 'OwnerID') and pet.OwnerID != '0':
            await self.bot.say("This User is already adopted!")
            return

        elif owner and ((owner.PetAmount+1)*10) - 10 > owner.Level:
            await self.bot.say("You cannot have any more Users right now.")
            return

        else:
            self.adoptions[arg.id] = ctx.message.author.id
            await self.bot.say(arg.name + " Do you accept the adoption? if so type ``wrig adopt accept``, ``wrig adopt decline`` otherwise.") 

    @adopt.command(name='accept', pass_context=True)
    async def _accept(self, ctx):

        try:
            oID = self.adoptions[ctx.message.author.id]
        except KeyError:
            await self.bot.say("You are not up for adoption right now.")
            return
        
        try:
            owner = self.session.query(Owner).filter(Owner.OwnerID == oID).one()
        except:
            owner = None
        
        try:
            pet = self.session.query(Pet).filter(Pet.PetID == ctx.message.author.id).one()
        except:
            pet = None

        if not owner:
            new_owner = Owner(OwnerID = oID, PetAmount = 1, Level = 1, Experience = 0, OwnerFriendlyName = discord.utils.get(ctx.message.server.members, id=oID).name, ServerID = ctx.message.server.id)
            self.session.add(new_owner)
            self.session.commit()
        else:
            owner.PetAmount += 1
            self.session.commit()
        if pet == None: 
            new_pet = Pet(PetID = ctx.message.author.id, PetFriendlyName = ctx.message.author.name, ServerID = ctx.message.server.id,
                          AttribATK = 10, AttribDEF = 10, AttribHP = 20, AttribPTS = 0, AttribATKPTS = 0, AttribACCPTS = 0,
                          AttribLCK = .01, AttribACC = .8, AttribEVA = .05, AttribHPPTS = 0, AttribLCKPTS = 0, 
                          Level = 0, Experience = 0, OwnerID = oID,  AttribDEFPTS = 0, AttribEVAPTS = 0)
            
            self.session.add(new_pet)
            self.session.commit()
        
        else:
            pet.OwnerID = oID
            self.session.commit()

        del self.adoptions[ctx.message.author.id]
        await self.bot.say("{0} has been adopted by <@{1}>!".format(ctx.message.author.name, oID))
        
    @adopt.command(name="decline", pass_context=True)
    async def _decline(self, ctx):
        try:
            oID = self.adoptions[ctx.message.author.id]
        except KeyError:
            await self.bot.say("You are not up for adoption right now.")
            return
        
        del self.adoptions[ctx.message.author.id]
        await self.bot.say("You were not adopted.")


    @commands.command(pass_context=True)
    async def abandon(self, ctx, arg : discord.User):
        try:
            owner = self.session.query(Owner).filter(Owner.OwnerID == ctx.message.author.id).one()
        except:
            owner = None

        try:
            pet = self.session.query(Pet).filter(Pet.PetID == arg.id, Pet.OwnerID == ctx.message.author.id).one()
        except:
            pet = None

        if not owner or owner.PetAmount == 0:
            await self.bot.say("You do not have anyone to abandon")
        elif not pet:
            await self.bot.say("You cannot abandon someone you don't own!")
        else:
            owner.PetAmount-=1
            pet.OwnerID = 0
            self.session.commit()
            await self.bot.say("{0} has abandoned {1}, in the rain, alone.".format(owner.OwnerFriendlyName,  pet.PetFriendlyName))

    @commands.command(pass_context=True)
    async def pets(self, ctx):

        pets = []        

        try:
            petlist = self.session.query(Pet).filter(Pet.OwnerID == ctx.message.author.id).all()
        except:
            await self.bot.say("You do not have any pets.")
            return
        
        for pet in petlist:
             pets.append(pet.PetFriendlyName)
         
        await self.bot.say("<@{}>'s Pets are: \n{}".format(ctx.message.author.id, str.join("\n", pets)))

    @commands.command(pass_context=True)
    async def flee(self, ctx):
        try:
            pet = self.session.query(Pet).filter(Pet.PetID == ctx.message.author.id).one()
            owner = self.session.query(Owner).filter(Owner.OwnerID == pet.OwnerID).one()
        except Exception as e:
            print(e)
            await self.bot.say("You are not currently owned by anyone.")
            return

        pet.OwnerID = 0
        owner.PetAmount -= 1
        self.session.commit()
        
        await self.bot.say("You have ran away from {}. You are free.".format(owner.OwnerFriendlyName))
        
        self.session.close()

def setup(bot):
    bot.add_cog(PetClaim(bot))