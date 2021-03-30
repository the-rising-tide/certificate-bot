import logging

# core interface to the database
from sqlalchemy import create_engine, DateTime
# base contains a metaclass that produces the right table
from sqlalchemy.ext.declarative import declarative_base
# setting up a class that represents our SQL Database
from sqlalchemy import Column, Integer, String, Boolean, DateTime
# prints if a table was created - neat check for making sure nothing is overwritten
from sqlalchemy import event

engine = create_engine('sqlite:///data/main.db', echo=True)
Base: declarative_base = declarative_base()


class Users(Base):
    __tablename__ = 'USERS'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    username = Column(String)
    add_mode = Column(Boolean)  # True: add domains, False: delete domains

    def __repr__(self):
        return f"<UsersEntry: username='{self.username}', chat_id='{self.chat_id}', " \
               f"primary_key='{self.id}'"


class Domains(Base):
    __tablename__ = 'DOMAINS'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    domain = Column(String)
    port = Column(String)
    # expiry_date = Column(Date)
    last_checked = Column(DateTime)
    issuer = Column(String)
    not_before = Column(DateTime)
    not_after = Column(DateTime)

    def __repr__(self):
        return f"<DomainsEntry: chat_id='{self.chat_id}', domain='{self.domain}', port='{self.port}'," \
               f" last_time_checked='{self.last_checked}, primary_key='{self.id}'"


@event.listens_for(Base.metadata, 'after_create')
def receive_after_create(target, connection, tables, **kw):
    """listen for the 'after_create' event"""
    logging.info('A table was created' if tables else 'No table was created')
    print('A table was created' if tables else 'No table was created')


# creating db which doesn't happen when it should?
database = Base.metadata.create_all(bind=engine)
