import os
from typing import List, Union

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Row
from sqlalchemy import create_engine, select, update

from telegram import Update, CallbackQuery
from telegram.ext import CallbackContext
from telegram.error import BadRequest

import core.db_models as dbm
import commands.keyboards as kb
import utils.utils as utl

engine = create_engine('sqlite:///data/main.db', echo=True)


def get_entries_by_chat_id(chat_id: int, database=dbm.Domains) -> List[Union[dbm.Domains, dbm.Users]]:
    """
    :param chat_id: telegram chat id
    :param database: Reference to model class of database to be accessed\n
    e.g. database.Users
    :return: List of all matching entries as Objects of given database model
    """

    # get entries from entered database
    session = sessionmaker(bind=engine)()
    statement: List[Row] = select(database).where(database.chat_id == chat_id)
    # extract entry objects from row objects
    entries = [e[0] for e in session.execute(statement).all()]
    return entries


def toggle_add(query: CallbackQuery, state: bool):
    """
    :param query:
    :param state: True: add mode, False: delete mode
    Toggle between add and delete mode
    :return:
    """
    stmt = (update(dbm.Users)).where(dbm.Users.chat_id == query.message.chat_id).values(add_mode=state)
    session = sessionmaker(bind=engine)()
    session.execute(stmt)
    session.commit()
    if state:
        mode = 'add'
    else:
        mode = 'delete'
    text = utl.prep_for_md(f"You're in *{mode} mode*\n"
                           "Simply send domains to add in the chat.\nAssuming port 443 if no explicit port is given.\n"
                           "Example: sub.example.com:3145", ignore=['*'])
    try:
        query.edit_message_text(text, reply_markup=kb.main_menu, parse_mode='MarkdownV2')
    except BadRequest as e:
        # TODO: Handle bad request when my-list button is clicked again -> ignore that command in query?
        print("Bad request")
        print(e)


def watchlist_to_csv(query: CallbackQuery, entries=None) -> str:
    """
    :param query: invoked Callback Query
    :param entries: optional - list of entry objects if already queried
    Makes csv file tmp/(chat_id).csv\n
    - creates tmp/ if not exists
    :return: Path to file
    """
    if not entries:  # query entries if not given
        entries = get_entries_by_chat_id(query.message.chat_id)

    # make csv string
    response = 'domain;port;notAfter;notBefore;issuer;lastChecked\n'
    for e in entries:
        response += f'{e.domain};{e.port};{e.not_after};{e.not_before};{e.issuer};{e.last_checked}\n'

    if not os.path.exists('tmp/'):
        os.mkdir('tmp/')

    path = f'tmp/{query.message.chat_id}.csv'
    with open(path, 'w') as f:
        f.write(response)

    return path


def export_watchlist(query: CallbackQuery):
    path = watchlist_to_csv(query)
    with open(path, 'r') as f:
        query.edit_message_text("Here you go:")
        query.message.chat.send_document(f)


def display_watchlist(query: CallbackQuery):
    """
    :param query: Invoked Query
    Inline command for display of all watched domains\n
    Sends csv file if too many characters (4096 chars)
    :return: None
    """
    # get entries
    entries = get_entries_by_chat_id(query.message.chat.id)

    # build answer string
    response = "__Your watched domains__:\n\n"
    for e in entries:
        response += f"https://{e.domain}:{e.port} \nexpiry: *{e.not_after.date()}* - last checked {e.last_checked.replace(microsecond=0)}\n\n"

    resp = utl.prep_for_md(response, ignore=['*', '_'])
    print(resp)
    # catch too long messages - transition to sending csv file
    if len(resp) > 4096:
        file = watchlist_to_csv(query, entries)

        with open(file, 'r') as f:
            query.edit_message_text("The list is too long for display - here you go:")
            query.message.chat.send_document(f)

        return

    try:
        query.edit_message_text(resp, reply_markup=kb.main_menu, parse_mode='MarkdownV2')

    except BadRequest as e:
        # TODO: Handle bad request when my-list button is clicked again -> ignore that command in query?
        print("Bad request")
        print(e)
        query.edit_message_text(response, reply_markup=kb.main_menu)
