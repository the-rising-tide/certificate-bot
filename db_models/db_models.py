# core interface to the database
from sqlalchemy import create_engine
# base contains a metaclass that produces the right table
from sqlalchemy.ext.declarative import declarative_base
# setting up a class that represents our SQL Database
from sqlalchemy import Column, Integer, String, Date
# prints if a table was created - neat check for making sure nothing is overwritten
from sqlalchemy import event

engine = create_engine('sqlite:///data/main.db', echo=True)
Base: declarative_base = declarative_base()


class Users(Base):
    __tablename__ = 'USERS'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    username = Column(String)

    def __repr__(self):
        return f"<MainDB: username='{self.username}', chat_id='{self.chat_id}', " \
               f"primary_key='{self.id}'"


class Domains(Base):
    __tablename__ = 'DOMAINS'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    domain = Column(String)
    expiry_date = Column(Date)
    last_checked = Column(Date)

    def __repr__(self):
        return f"<MainDB: chat_id='{self.chat_id}', domain='{self.domain}', saved_expiry='{self.expiry_date}'," \
               f" last_time_checked='{self.last_checked}, primary_key='{self.id}'"


@event.listens_for(Base.metadata, 'after_create')
def receive_after_create(target, connection, tables, **kw):
    """listen for the 'after_create' event"""
    print('A table was created' if tables else 'No table was created')


# creating db which doesn't happen when it should?
database = Base.metadata.create_all(bind=engine)
