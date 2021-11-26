import gspread
from config import SETTINGS


def get_table():
    try:
        gc = gspread.service_account(filename='chat-control-bot-51ee946bff60.json')
        sh = gc.open(SETTINGS['google']['table_name'])
        worksheet = sh.worksheet(SETTINGS['google']['worksheet_name'])
        list_of_lists = worksheet.get_all_records()

        for item in list_of_lists:
            item['private'] = True if item['private'] == 'TRUE' else False

        print('Data from google spreadsheet loaded')
        return list_of_lists
    except Exception as exc:
        print("google spreadsheet: "+str(exc))
        return {}

