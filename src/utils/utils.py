from configparser import ConfigParser
from typing import Union, List

from telegram import Update, CallbackQuery
from telegram.ext import CallbackContext

import core.db_models as dbm

def send_msg(update: Union[Update, CallbackQuery], context: CallbackContext, text, keyboard=None, parse_mode=''):
    if parse_mode == 'md':
        parse_mode = 'MarkdownV2'
    context.bot.send_message(chat_id=update.message.chat_id,
                             reply_markup=keyboard,
                             text=text,
                             parse_mode=parse_mode)


config = ConfigParser()
config.read("settings.ini")
NOTIFY_BEFORE = int(config['settings']['NOTIFY_BEFORE'])


def prep_for_md(text: str, ignore=None) -> str:
    """
    :param text: string to be treated
    :param ignore: List with symbols (str) that shall not be replaced
    :return: string with escaped symbols

    - Escapes all symbols that have a special meaning in telegrams MarkdownV2\n
    - Selected symbols can be ignored by passing them into the function as list\n
    e.g. ['*', '_'] those symbols will not be escaped to be interpreted as italics / bold\n

    See: https://core.telegram.org/bots/api#markdownv2-style
    """

    symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    if ignore:
        for s in ignore:
            symbols.remove(s)

    for s in symbols:
        # print(f'{s}', '\{}'.format(s))
        text = text.replace(f'{s}', '\{}'.format(s))
    return text


def mk_link(link: str, port: Union[str, int]) -> str:
    """evaluate whether port should be shown or not"""
    return f'https://{link}:{port}' if str(port) != '443' else f'https://{link}'


def sort_by_expiry(entries: List[dbm.Domains], reverse=False) -> List[dbm.Domains]:
    """
    :param entries: List of domain entries
    :param reverse: Flips order if true (latest to expire first)
    Sort entries by expiry date (first to expire comes first)
    :return: Sorted list
    """
    return sorted(entries, key=lambda entry: entry.not_after, reverse=reverse)


def get_help_text() -> str:
    """:return: central help text in markdown style"""
    return prep_for_md('__*Track the certificates of your domains*__\n\n'
                       'Simply send a domain in the chat and it will be tracked.\n\n'
                       "You'll be notified when one or more of the following cases occur:\n\n"
                       '- Changes of the start or expiry date of your certificate\n'
                       f'- Your cert is only valid for less than {NOTIFY_BEFORE} days\n\n'
                       'All registered domains will be checked once a day.\n'
                       "To remove a domain from the list use the _Delete entry_ button to toggle deletion mode.\n\n"
                       "Please visit https://github.com/the-rising-tide/certificate-bot to report any issues",
                       ignore=['_', '*'])

# month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
# # generate a dict of the scheme 'Jan': 01 - 'Dec': '12'
# mon_abrev_dict = {abrev: f'0{count + 1}' if count < 10 else f'{count + 1}' for count, abrev in enumerate(month_list)}
