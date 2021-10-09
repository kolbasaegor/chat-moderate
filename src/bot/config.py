from os import environ

SETTINGS = {
    'session_manager': {
        'default_lang': 'ru',
        'default_state': 'start',
        'default_tree_id': 'default',
        'default_state_id': 'tree_default'
    },
    'db': {
        'host': environ.get('DB_HOST', 'localhost'),
        'port': int(environ.get('DB_PORT', '27017')),
        'name': environ.get('DB_NAME', 'test_bot_db'),
    },
    'bot': {
        'token': environ.get('BOT_TOKEN', None)
    }
}
