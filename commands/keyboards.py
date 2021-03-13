from telegram import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = InlineKeyboardMarkup([[InlineKeyboardButton('My watchlist', callback_data='watchlist'),
                                   InlineKeyboardButton('Register new', callback_data='new_registration'),
                                   InlineKeyboardButton('Delete entry', callback_data='delete_entry')]])

# TODO: Write register keyboards

# TODO: Generate delete keyboard (each domain one button - callback is key of database line)
# TODO: Generate oversight (each domain on
# TODO: Implement upwards buttons

# TODO: Future: Generate oversight deeper look?
