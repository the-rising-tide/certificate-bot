import os
import logging
import threading
import time
from datetime import datetime

from telegram import Bot
from telegram import error
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters

# core interface to the database
from sqlalchemy import create_engine
# base contains a metaclass that produces the right table
from sqlalchemy.ext.declarative import declarative_base
# this custom session class will create new session objects bound to our database
# it will receive one of multiple connections from the engine and holds on to it until committing or closing
from sqlalchemy.orm import sessionmaker

import commands.user_commands as cmd
import commands.on_message as on_msg
import core.cycle_certs as cycle
import core.db_models as dbm

logging.basicConfig(
    filename="events.log",
    level=logging.INFO,
    style="{",
    format="[{asctime}] [{levelname}] [{name}] {message}")

engine = create_engine('sqlite:///data/main.db', echo=True)
Base: declarative_base = declarative_base()

# initializing new session
Session = sessionmaker(bind=engine)
session = Session()

API_Key = os.environ["API_KEY"]

updater = Updater(API_Key, use_context=True)
dispatcher = updater.dispatcher

bot = Bot(token=API_Key)


def request_daily():
    """
    Issues cert handling and dispatches updates after requests are finished
    """
    while True:
        updates = cycle.cycle_certs()
        logging.info(f'Starting dispatch of {len(updates)} updates')
        for update in updates:
            chat_id = update[0]
            try:
                bot.send_message(chat_id, update[1], parse_mode='MarkdownV2')
            # if bot is blocked - cleaning database
            except error.Unauthorized:
                logging.info(f'Blocked by {chat_id} - removing affiliated entries from Users and Domains DB')
                session.query(dbm.Users).filter(dbm.Users.chat_id == chat_id).delete()
                session.query(dbm.Domains).filter(dbm.Domains.chat_id == chat_id).delete()
                session.commit()
            # block that makes sure that 30 messages per second aren't exceeded
            time.sleep(0.04)

        logging.info("Finished dispatch of updates, sleeping now")
        # sleeping until next day
        d = datetime.now()
        till_tomorrow = ((24 - d.hour - 1) * 60 * 60) + \
                        ((60 - d.minute - 1) * 60) + \
                        (60 - d.second) + \
                        (3600 * 6)  # earliest request starts at 6 am
        time.sleep(till_tomorrow)


# start thread for cert requests
cert_thread = threading.Thread(target=request_daily).start()

dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), on_msg.handle_message))

dispatcher.add_handler(CommandHandler(['start'], cmd.start))

# responsible for all inline commands
dispatcher.add_handler(CallbackQueryHandler(cmd.handle_callback))

updater.start_polling()
updater.idle()
