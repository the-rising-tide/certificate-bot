import logging
import traceback

from telegram import Update, CallbackQuery, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from sqlalchemy.orm import sessionmaker
# core interface to the database
from sqlalchemy import create_engine, select

import core.db_models as dbm
import commands.keyboards as kb
import utils.utils as utl
import commands.inline_commands as incmd

engine = create_engine('sqlite:///data/main.db', echo=True)


def start(update: Update, context: CallbackContext):
    session = sessionmaker(bind=engine)()
    # prevent double entries
    # if return has entries - user is in database
    if incmd.get_entries_by_chat_id(update.message.chat_id, database=dbm.Users):
        utl.send_msg(update, context, f"You're already registered.\nYou ID is {update.message.chat_id}")
        return

    # add new user to database
    user = dbm.Users(chat_id=update.message.chat.id, username=update.message.chat.username, add_mode=True)
    session.add(user)
    session.commit()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Hi, you're now registered!\n"
             f"This bot can watch your certificates and will notify you {utl.NOTIFY_BEFORE} days before the certificate expires.\n"
             f"Your ID is: {update.message.chat.id}",
        reply_markup=kb.main_menu)


def handle_callback(update: Update, context: CallbackContext):
    """
    :param update:
    :param context:
    Main handler for callback queries:\n
    - maps queries to matching command

    - handles 'query prefixes' like 'clear_' to clear inline keyboards
    - sends new message at the end, if needed
    :return:
    """
    command_switch = {
        'watchlist': incmd.display_watchlist,
        'export_csv': incmd.export_watchlist,
    }

    # extract callback object
    query: CallbackQuery = update.callback_query
    query.answer()
    key = query.data

    print("Got key", key)

    if key.startswith('clear_'):
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[]]))
        key = key.replace('clear_', '')

    send_new_message = False  # to toggle a new message at the end
    if key.startswith('new_'):
        key = key.replace('new_', '')
        send_new_message = True

    # mode toggle needs extra input - catch before switch
    if key == 'add_entry':
        incmd.toggle_add(query, True)
        return

    elif key == 'delete_entry':
        incmd.toggle_add(query, False)
        return

    # if key.startswith('watchlist'):
    #     command_switch['watchlist'](query, update, context)

    try:
        # try to extract command
        command = command_switch[key]
        # check if command belongs to inline commands
        if command.__module__ == 'commands.inline_commands':
            command(query)

        # else:
        #     command(update, context)

        # send new menu if toggled
        if send_new_message:
            utl.send_msg(query, context, "What's next?", keyboard=kb.main_menu)

    # if we fail to extract the key
    except KeyError:
        logging.error(f"CAN'T FIND COMMAND {key} IN COMMAND_SWITCH\n{traceback.format_exc()}")
        print(f'{key} was NOT listed!')


def send_help(update: Update, context: CallbackContext):
    utl.send_msg(update, context, utl.get_help_text(), keyboard=kb.main_menu, parse_mode='MarkdownV2')
