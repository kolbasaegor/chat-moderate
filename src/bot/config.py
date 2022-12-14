from os import environ

SETTINGS = {
    'session_manager': {
        'default_lang': 'en',
        'default_state': 'start',
        'default_tree_id': 'default',
        'default_state_id': 'tree_default',
        'default_page': 0
    },
    'db': {
        'host': environ.get('DB_HOST', 'localhost'),
        'port': int(environ.get('DB_PORT', '27017')),
        'name': environ.get('DB_NAME', 'test_bot_db'),
    },
    'bot': {
        'token': '2052260074:AAFkFTV1xPjar2oQj2ww9YK67cnM5qRcIu4',
        'num_of_displayed_pages': 3,
        'concierge_id': 1520938471,
        'empty_photo': 'https://sun9-44.userapi.com/impf/UT2_NBbLENA0qRLjwILib--M_SX208dpJRo_2g/bwqkwLFpaek.jpg?size=604x506&quality=96&sign=69cfd67295d6988cd6079b5191ff8c22&c_uniq_tag=71gRlLH-2k67ZXlr-TjTleHZX0IV8ygLi2qx-mDGbVc&type=album',
        'expire_days': 1,
        'member_limit': 1,
        # interval in seconds
        'interval': 60,
        'delay': 1,
        'password_for_update': 'b3br4'
    },
    'google': {
        'gmail': 'botik-chat@chat-control-bot.iam.gserviceaccount.com',
        'table_name': 'Chats',
        'worksheet_name': 'Лист1',
        # update_time in seconds
        'update_time': 3600
    }
}
