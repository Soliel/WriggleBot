import discord
import sqlalchemy
from discord.ext import commands
from Scripts.DataPy.DataObjects import Base, Pet, Owner
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class PetClaim():

    def __init__(self, bot):
        self.bot = bot
    
    adoptions = {}

    @commands.group(pass_context=True, invoke_without_command=True)
    async def adopt(self, ctx, arg : discord.User):
        
        engine = create_engine('sqlite:///Data\{}.db'.format(ctx.message.server.id))
        Base.metadata.bind = engine
        Base.metadata.create_all(engine)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        owner = session.query(Owner).filter(Owner.OwnerID == ctx.message.author.id).one()

        if arg.id == ctx.message.author.id:
            await self.bot.say("You cannot adopt yourself!")
            session.close()
            return

        elif session.query(Pet).filter(Pet.PetID == arg.id).all() != []:
            await self.bot.say("This User is already adopted!")
            session.close()
            return

        elif (owner.PetAmount+1)*10 > owner.Level:
            await self.bot.say("You cannot have any more Users right now.")
            session.close()
            return

        else:
            self.adoptions[arg.id] = ctx.message.author.id
            await self.bot.say(arg.mention + " Do you accept the adoption? if so type ``~adopt accept``, ``~adopt decline`` otherwise.") 

    @adopt.command(name='accept', pass_context=True)
    async def _accept(self, ctx):
        
        engine = create_engine('sqlite:///Data\{}.db'.format(ctx.message.server.id))
        Base.metadata.bind = engine
        Base.metadata.create_all(engine)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        owner = session.query(Owner).filter(Owner.OwnerID == ctx.message.author.id).one()
        
        try:
            oID = self.adoptions[ctx.message.author.id]
        except KeyError:
            await self.bot.say("You are not up for adoption right now.")
            session.close()
            return

        owner = session.query(Owner).filter(Owner.OwnerID == oID).one()

        if owner == []:
            new_owner = Owner(OwnerID = oID, PetAmount = 1, Level = 1, OwnerFriendlyName = discord.utils.get(ctx.message.server.members, id=oID).name)
            session.add(new_owner)
        else:
            session.execute("UPDATE OwnerTable SET PetAmount=:param WHERE OwnerID=:param2", {"param":owner.PetAmount+1, "param2":oID})
        
        new_pet = Pet(PetID = ctx.message.author.id, PetFriendlyName = ctx.message.author.name,
                      AttribATK = 10, AttribDEF = 10, AttribHP = 20,
                      AttribLCK = .01, AttribACC = .8, AttribEVA = .05,
                      Level = 0, OwnerID = oID)

        session.add(new_pet)
        session.commit()
        session.close()

        del self.adoptions[ctx.message.author.id]
        await self.bot.say("<@{0}> has been adopted by <@{1}>!".format(ctx.message.author.id, oID))
        
    @adopt.command(name="decline", pass_context=True)
    async def _decline(self, ctx):
        try:
            oID = self.adoptions[ctx.message.author.id]
        except KeyError:
            await self.bot.say("You are not up for adoption right now.")
            return
        
        del self.adoptions[ctx.message.author.id]
        await self.bot.say("You were not adopted.")

def setup(bot):
    bot.add_cog(PetClaim(bot))