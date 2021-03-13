from telegram import Update
from telegram.ext import CallbackContext

from sqlalchemy.orm import sessionmaker
# core interface to the database
from sqlalchemy import create_engine

from db_models.db_models import Users
import commands.keyboards as kb

engine = create_engine('sqlite:///data/main.db', echo=True)


def start(update: Update, context: CallbackContext):
    user = Users(chat_id=update.message.chat.id, username=update.message.chat.username)
    session = sessionmaker(bind=engine)()
    # TODO: Prevent double entries
    session.add(user)
    session.commit()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Hi, you're now registered!\nYour ID is: {update.message.chat.id}",
        reply_markup=kb.main_menu)

# TODO: Register command

# TODO: Callback handler
    # TODO: Delete function
    # TODO: Oversight function
