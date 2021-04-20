import logging
import traceback
from typing import List, Union

from sqlalchemy.engine import Row
from telegram import Update, CallbackQuery, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from sqlalchemy.orm import sessionmaker
# core interface to the database
from sqlalchemy import create_engine, select, delete

import core.db_models as dbm
import commands.keyboards as kb
import utils.utils as utl
import commands.inline_commands as incmd

engine = create_engine('sqlite:///data/main.db', echo=True)

logger = logging.getLogger('cert-bot')


def start(update: Update, context: CallbackContext):
    session = sessionmaker(bind=engine)()
    # prevent double entries
    # if return has entries - user is in database
    if incmd.get_entries_by_chat_id(update.message.chat_id, database=dbm.Users):
        utl.send_msg(
            update, context,
            text=utl.prep_for_md(f"Hey, you're already registered.\nYou ID is: {update.message.chat_id}\n\n") +
            utl.get_help_text(),
            keyboard=kb.main_menu, parse_mode='MarkdownV2')
        return

    # add new user to database
    user = dbm.Users(chat_id=update.message.chat.id, username=update.message.chat.username, menu='main', add_mode=True)
    session.add(user)
    session.commit()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=utl.prep_for_md(f"Hi, you're now registered!\n" f"Your ID is: {update.message.chat.id}\n\n") +
        utl.get_help_text(),
        reply_markup=kb.main_menu, parse_mode='MarkdownV2')


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
        'back': incmd.main_menu,  # functional but not implemented -> keyboards.py
        'more': incmd.more_menu,  # functional but not implemented -> keyboards.py
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
        logger.error(f"CAN'T FIND COMMAND {key} IN COMMAND_SWITCH\n{traceback.format_exc()}")
        print(f'{key} was NOT listed!')


def send_help(update: Update, context: CallbackContext):
    utl.send_msg(update, context, utl.get_help_text(), keyboard=kb.main_menu, parse_mode='MarkdownV2')


def get_main_menu(chat_id: Union[str, int]) -> str:
    """:returns: main menu text in markdown format including some information about the current state of the user"""
    # locate user in db
    session = sessionmaker(bind=engine)()
    statement: List[Row] = select(dbm.Users).where(dbm.Users.chat_id == int(chat_id))
    entry: dbm.Users = session.execute(statement).first()[0]  # its a Tuple
    mode = '_add domain mode_ - send a domain and it will be tracked' if entry.add_mode \
        else '_delete domain mode_ - send a domain and it will be removed from you list'
    return utl.prep_for_md(
            f'This is the main menu:\n'
            f"You're currently in {mode}.\n\n"
            f'Your ID: {entry.chat_id}\n', ignore=['_'])


def send_menu(update: Update, context: CallbackContext):
    """Sends a main menu and some information about the current state of the user"""
    utl.send_msg(
        update, context,
        get_main_menu(update.message.chat_id),
        keyboard=kb.main_menu, parse_mode='MarkdownV2')


def wipe_all(update: Update, context: CallbackContext):
    args = update.message.text.split()  # first arg is command itself

    # python seems to evaluate from left to right, so len() handles the case that no second param is gievn
    if len(args) == 1 or args[1] != 'ALL':
        utl.send_msg(update, context,
                     utl.prep_for_md(f"Enter `{args[0]} ALL` to delete *all* tracked entries", ignore=['*', '`']),
                     keyboard=kb.main_menu, parse_mode='MarkdownV2')
    else:
        # we're good to go - delete all entries of that user from database
        session = sessionmaker(bind=engine)()
        statement = delete(dbm.Domains).where(dbm.Domains.chat_id == update.message.chat_id)
        session.execute(statement)
        session.commit()
        incmd.toggle_add(update, True)  # set user to add mode, he doesn't have anything delete anymore ;)
        utl.send_msg(update, context, utl.prep_for_md("Success: All your entries are wiped.\nYou're now in _add mode_",
                                                      ignore=['_']), keyboard=kb.main_menu, parse_mode='MarkdownV2')