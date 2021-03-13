import os

from telegram import Bot
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler

# core interface to the database
from sqlalchemy import create_engine
# base contains a metaclass that produces the right table
from sqlalchemy.ext.declarative import declarative_base
# this custom session class will create new session objects bound to our database
# it will receive one of multiple connections from the engine and holds on to it until committing or closing
from sqlalchemy.orm import sessionmaker

import db_models.db_models as db_models
import commands.user_commands as cmd

engine = create_engine('sqlite:///data/main.db', echo=True)
Base: declarative_base = declarative_base()

# initializing new session
Session = sessionmaker(bind=engine)
session = Session()

API_Key = os.environ["API_KEY"]

updater = Updater(API_Key, use_context=True)
dispatcher = updater.dispatcher

bot = Bot(token=API_Key)

dispatcher.add_handler(CommandHandler(['start'], cmd.start))

updater.start_polling()
updater.idle()
