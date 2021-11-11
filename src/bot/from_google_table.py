import gspread
from config import SETTINGS


def get_table():
    gc = gspread.service_account(filename='chat-control-bot-51ee946bff60.json')
    sh = gc.open(SETTINGS['google']['table_name'])
    worksheet = sh.get_worksheet(0)
    list_of_lists = worksheet.get_all_records()

    for item in list_of_lists:
        item['private'] = True if item['private'] == 'TRUE' else False

    return list_of_lists
