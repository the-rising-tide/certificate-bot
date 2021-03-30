import re
import logging
from datetime import datetime
from typing import Dict, Union

from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker
from telegram import Update, CallbackQuery
from telegram.ext import CallbackContext
import dateparser

import commands.keyboards as kb
import utils.utils as utl
import core.request_cert as req_ct
from core import db_models as dbm
from commands.inline_commands import get_entries_by_chat_id

engine = create_engine('sqlite:///data/main.db', echo=True)


def is_domain(link: str) -> Dict[str, Union[str, bool]]:
    link.replace("https://", "")
    # pattern that describes a domain including subdomains and port
    # group 0: whole link
    # group 1: whole domain (without port)
    # group 2: subdomains e.g. 'my.sub.'example.com
    # group 3: main domain sub.'example.com'
    # group 4: port example.com':31415'
    pattern = re.compile(r"(((?:[a-z0-9-]+\.)*)([a-z0-9-]+\.[a-z]+))($|\s|:\d{1,5})")
    result = pattern.search(link)
    if not result:
        print(f"'{link}' is no valid domain")
        return {}

    results = {
        'whole_link': result.group(0),
        'domain': result.group(1),
        'sub_domain': result.group(2),
        'top_domain': result.group(3),
        # registering whether a port was specified
        'port_given': True if result.group(4) else False,
        # setting default port if nothing was specified
        'port': result.group(4)[1:] if result.group(4) else '443',
    }

    return results


def handle_message(update: Update, context: CallbackContext):
    """
    :param update: Telegram Update Object
    :param context: Telegram CallBackContext Object
    Handle messages sent to the bot.\n
    Detect whether user is in add or delete mode\n
    - scan for valid domains in message\n

    On delete mode:\n
    - remove extracted domain from database for this user

    On add mode:\n
    - request certificate to ensure domain is valid
    - add to database

    :return:
    """

    # validate that domain is syntactically correct
    domain_input = is_domain(update.message.text)
    if not domain_input:
        utl.send_msg(update, context, "Hey, this is no valid domain input!\n"
                                      "A valid domain would be sub.example.com:443", keyboard=kb.main_menu)
        return False

    # init session to find user
    session = sessionmaker(bind=engine)()
    user = get_entries_by_chat_id(update.message.chat_id, database=dbm.Users)[0]

    # read out which mode user is in
    # add_mode == False means delete mode
    # delete entry and return
    if not user.add_mode:
        stmt = (delete(dbm.Domains).where(dbm.Domains.domain == domain_input['domain']
                                          and dbm.Domains.port == domain_input['port']
                                          and dbm.Domains.chat_id == update.message.chat_id))
        session.execute(stmt)
        session.commit()
        text = utl.prep_for_md(f"You're in *delete mode*:\n"
                               f"{domain_input['domain']} - Port: {domain_input['port']} is no longer tracked for you",
                               ignore=['*'])
        utl.send_msg(update, context, text,
                     keyboard=kb.main_menu, parse_mode='MarkdownV2')
        return

    # continue with add process

    # request cert - returning if it fails
    print("requesting")

    cert = req_ct.get_cert(domain_input['domain'], domain_input['port'])
    print("done")

    if not cert:
        utl.send_msg(update, context, "This domain is syntactically correct, but there is no certificate.",
                     keyboard=kb.main_menu)
        return False

    # check if that user already registered that domain
    statement = select(dbm.Domains).where(dbm.Domains.domain == domain_input['domain']
                                          and dbm.Domains.port == domain_input['port']
                                          and dbm.Domains.chat_id == update.message.chat_id)

    if session.execute(statement).all():
        print("Search:", session.execute(statement).all())
        utl.send_msg(update, context, "This domain is already tracked for you", kb.main_menu)
        return

    # add new entry
    valid_until = dateparser.parse(cert['notAfter'])
    entry = dbm.Domains(chat_id=update.message.chat_id,
                        domain=domain_input['domain'],
                        port=domain_input['port'],
                        # expiry_date=cert['notAfter'],
                        last_checked=datetime.today(),
                        issuer=cert['caIssuers'][0],
                        not_before=dateparser.parse(cert['notBefore']),
                        not_after=valid_until,
                        )

    session.add(entry)
    session.commit()

    text = utl.prep_for_md(f"You're in *add mode*:\n"
                           f"Your domain {domain_input['domain']} - Port:{domain_input['port']} is registered.\n"
                           f"The current cert is active until: {valid_until}", ignore=['*'])
    utl.send_msg(update, context, text, keyboard=kb.main_menu, parse_mode='MarkdownV2')


if __name__ == '__main__':
    print(is_domain("hjfd"))
