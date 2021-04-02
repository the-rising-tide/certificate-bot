from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# prefixes (to be used in this order only)
# clear_ clear inline keyboard on current message
# new_ send a new main menu when command was executed
main_menu = InlineKeyboardMarkup([[InlineKeyboardButton('My watchlist', callback_data='watchlist'),
                                   InlineKeyboardButton('Register new', callback_data='add_entry'),
                                   InlineKeyboardButton('Delete entry', callback_data='delete_entry'),
                                   InlineKeyboardButton('Export data', callback_data='clear_new_export_csv'),
                                   # Sub menu not activated
                                   # InlineKeyboardButton('More', callback_data='more'),
                                   ]])

# From here: Completely functional sub-keyboard but not used
back_button = InlineKeyboardButton(u'\u2B05', callback_data='back')

more_menu = InlineKeyboardMarkup([[
    back_button,
    InlineKeyboardButton('Wipe entries', callback_data='wipe_all'),  # TODO: function wipe_all not implemented as inline
    InlineKeyboardButton('Export data', callback_data='clear_new_export_csv')]])

# implemented using 'My Watchlist' and 'export data'
# TODO: Generate delete keyboard (each domain one button - callback is key of database line)
# TODO: Generate oversight (each domain)
# TODO: Implement upwards buttons

# TODO: Future: Generate oversight deeper look?
