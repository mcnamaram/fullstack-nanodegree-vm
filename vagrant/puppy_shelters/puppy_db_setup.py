import enum
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import Date, Enum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class GenderEnum(enum.Enum):
    """Valid genders are (M)ale, (F)emale, and (N)euter"""
    male = 1
    female = 2
    neuter = 3


class Shelter(Base):
    __tablename__ = 'shelter'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    address = Column(String(250))
    city = Column(String(40))
    state = Column(String(20))
    zipCode = Column(String(10))
    website = Column(String)


class Puppy(Base):
    __tablename__ = 'puppy'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    date_of_birth = Column(Date)
    gender = Column('gender', Enum(GenderEnum))
    weight = Column(Numeric(10, 2))
    picture = Column(String)
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    shelter = relationship(Shelter)


engine = create_engine('sqlite:///puppyshelter.db')


Base.metadata.create_all(engine)
