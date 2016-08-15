from sqlalchemy import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.orm import *

Base = declarative_base()

class Owner(Base):
    __tablename__ = 'OwnerTable'
    OwnerID = Column(String(50), primary_key = True, nullable = False)
    OwnerFriendlyName = Column(String(50), nullable = False)
    ServerID = Column(String(50), nullable = False)
    PetAmount = Column(Integer)
    Level = Column(Integer)
    Experience = Column(Integer)
    BattleWins = Column(Integer)
    BattleLose = Column(Integer)
    BattlePlayed = Column(Integer)

class Pet(Base):
    __tablename__ = 'PetTable'
    PetID = Column(String(50), primary_key = True, nullable = False)
    PetFriendlyName = Column(String(50), nullable = False)
    ServerID = Column(String(50), nullable = False)
    AttribATK = Column(Integer)
    AttribDEF = Column(Integer)
    AttribHP = Column(Integer)
    AttribLCK = Column(Integer)
    AttribACC = Column(Integer)
    AttribEVA = Column(Integer)
    AttribPTS = Column(Integer)
    AttribATKPTS = Column(Integer)
    AttribDEFPTS = Column(Integer)
    AttribHPPTS = Column(Integer)
    AttribLCKPTS = Column(Integer)
    AttribACCPTS = Column(Integer)
    AttribEVAPTS = Column(Integer)
    Level = Column(Integer)
    Experience = Column(Integer)
    BattleWins = Column(Integer)
    BattleLose = Column(Integer)
    BattlePlayed = Column(Integer)
    OwnerID = Column(String(50), ForeignKey('OwnerTable.OwnerID'))
    owner = relationship(Owner)
