from sqlalchemy import create_engine, desc, asc, func
from sqlalchemy.orm import sessionmaker

from puppy_db_setup import Base, Shelter, Puppy
import datetime


engine = create_engine('sqlite:///puppyshelter.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


def query_all_puppies():
    """Query all of the puppies and return the results in ascending alphabetical order"""
    puppies = session.query(Puppy.name).order_by(asc(Puppy.name)).all()

    for puppy in puppies:
        print puppy.name


def query_young_puppies():
    """Query all of the puppies that are less than 6 months old organized by the youngest first"""
    today = datetime.date.today()
    # does not account for leap year
    sixMonthsPast = today - datetime.timedelta(days=(6 * (365 / 12)))
    youngPuppies = session.query(Puppy.name, Puppy.date_of_birth)\
        .order_by(desc(Puppy.date_of_birth))\
        .filter(Puppy.date_of_birth >= sixMonthsPast)

    for puppy in youngPuppies:
        print "{name}: {date}".format(name=puppy.name, date=puppy.date_of_birth)


def query_puppy_weights():
    """Query all puppies by ascending weight"""
    puppyWeights = session.query(Puppy.name, Puppy.weight)\
        .order_by(asc(Puppy.weight))\
        .all()

    for puppy in puppyWeights:
        print "{name}: {weight}".format(name=puppy.name, weight=puppy.weight)


def query_puppy_shelters():
    """Query all puppies grouped by the shelter in which they are staying"""
    # I first assumed a group_by clause, but that limits results to the first puppy
    # for each shelter (i.e. only 5 records returned).  After looking at the SQL I
    # would have written for the same task, I figured a simple order_by would work
    # here on shelter_id.
    puppyshelters = session.query(Puppy)\
        .join(Shelter)\
        .order_by(Puppy.shelter_id)

    # SELECT p.name, s.name
    # FROM Puppies p
    # JOIN Shelter s on p.shelter_id = s.id
    # ORDER_BY s.id

    for puppy in puppyshelters:
        print "{name}: {shelter}".format(name=puppy.name, shelter=puppy.shelter.name)


def query_puppy_shelters2():
    """(From solution file) Query all puppies grouped by the shelter in which they are staying"""
    # alternatively (from the training solution file)...
    # after running this example, I apparently misunderstood the expected result.
    # they wanted the count of puppies per facility...that makes sense
    puppyshelters = session.query(Shelter, func.count(Puppy.id))\
        .join(Puppy)\
        .group_by(Shelter.id)\
        .all()

    # ???
    # SELECT s.name, count(p.id)
    # FROM Shelter s
    # JOIN Puppy p on s.id = p.shelter_id
    # GROUP BY s.id

    for shelter in puppyshelters:
        print "{id} - {name} => {numPuppies}".format(id=shelter[0].id, name=shelter[0].name, numPuppies=shelter[1])
        # shelter[0].id, shelter[0].name, shelter[1]


query_puppy_shelters2()
