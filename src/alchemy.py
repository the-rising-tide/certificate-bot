"""
https://stackoverflow.com/questions/21766960/operationalerror-no-such-table-in-flask-with-sqlalchemy
For memory database
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite://", 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)
"""

# this thing is based on the tutorial from sqlalechemy
# https://docs.sqlalchemy.org/en/13/orm/tutorial.html#create-a-schema
import sqlalchemy
from datetime import datetime
import os

# core interface to the database
from sqlalchemy import create_engine

engine = create_engine('sqlite:///data/alchem.db', echo=True)

# base contains a metaclass that produces the right table
# see print(Base.metadata.create_all(engine))
from sqlalchemy.ext.declarative import declarative_base

Base: declarative_base = declarative_base()

# prints if a table was created - neat check for makling sure nothing is overwritten
from sqlalchemy import event


@event.listens_for(Base.metadata, 'after_create')
def receive_after_create(target, connection, tables, **kw):
    "listen for the 'after_create' event"
    print('A table was created' if tables else 'No table was created')


# setting up a class that represents our SQL Database
from sqlalchemy import Column, Integer, String, Date


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    date = Column(Date)

    def __repr__(self):
        return f"<User(name='{self.name}', fullname='{self.fullname}', nickname='{self.nickname}', date='{self.date}')>"


# creating db which doesn't happen when it should?
myretrun = Base.metadata.create_all(bind=engine)

# filling with an example object
ed_user = User(name="ed", fullname="ed euromaus", nickname="euro-mausi", date=datetime.now().date())

# this custom session class will create new session objects bound to our database
# it will recieve one of multiple connections from the engine and holds on to it until committing or closing
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

session = Session()  # initiating a new session

# adding our user to db "queue" - no SQL issued yet
session.add(ed_user)

our_user = session.query(User).filter_by(name='ed').first()
print(our_user)
#
edda_user = User(name="edda", fullname="edda euromaus", nickname="mausi", date=datetime.now().date())
fant_user = User(name="eurofant", fullname="eurofant eurofant", nickname="eurofanti", date=datetime.now().date())
session.add_all([edda_user, fant_user])

our_users = session.query(User).filter(User.name.in_(['ed', 'edda'])).all()
print("Our Users: ", our_users)
# session.commit()

# print(edda_user.id)

for instance in session.query(User).order_by(User.id):
    print(instance.name, instance.date)

# print(Base.metadata.create_all(engine))
