from typing import Union

from telegram import Update, CallbackQuery
from telegram.ext import CallbackContext


def send_msg(update: Union[Update, CallbackQuery], context: CallbackContext, text, keyboard=None, parse_mode=''):
    if parse_mode == 'md':
        parse_mode = 'MarkdownV2'
    context.bot.send_message(chat_id=update.message.chat_id,
                             reply_markup=keyboard,
                             text=text,
                             parse_mode=parse_mode)


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

# month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
# # generate a dict of the scheme 'Jan': 01 - 'Dec': '12'
# mon_abrev_dict = {abrev: f'0{count + 1}' if count < 10 else f'{count + 1}' for count, abrev in enumerate(month_list)}
