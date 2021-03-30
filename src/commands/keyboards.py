from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# prefixes (to be used in this order only)
# clear_ clear inline keyboard on current message
# new_ send a new main menu when command was executed
main_menu = InlineKeyboardMarkup([[InlineKeyboardButton('My watchlist', callback_data='watchlist'),
                                   InlineKeyboardButton('Register new', callback_data='add_entry'),
                                   InlineKeyboardButton('Delete entry', callback_data='delete_entry'),
                                   InlineKeyboardButton('Export data', callback_data='clear_new_export_csv')]])


# implemented using 'My Watchlist' and 'export data'
# TODO: Generate delete keyboard (each domain one button - callback is key of database line)
# TODO: Generate oversight (each domain)
# TODO: Implement upwards buttons

# TODO: Future: Generate oversight deeper look?
