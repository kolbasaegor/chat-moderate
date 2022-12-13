from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import datetime

class UserQManager(object):
    USERS_Q_COLLECTION = 'users_queue'
    IDS = 'users_ids'
    PRIVATE_CHATS = 'private_chats'
    _mongo_connection_timeout = 5

    def __init__(self, config):
        self._config = config

        client = MongoClient(config['db']['host'],
                             int(config['db']['port']),
                             serverSelectionTimeoutMS=self._mongo_connection_timeout)

        try:
            # force connect to check the connection
            client.server_info()

        except ServerSelectionTimeoutError as e:
            # notify and exit, if there are no available servers to connect
            print('Unable to connect to MongoDB within %d seconds. Error: "%s"\nStopped.' %
                  (self._mongo_connection_timeout, str(e)))

            exit(-1)

        else:
            print('Connected to Users Queue')

        self._db = client.get_database(config['db']['name'])
        self.users_collection = self._db.get_collection(UserQManager.USERS_Q_COLLECTION)
        self.users_ids = self._db.get_collection(UserQManager.IDS)
        if self.users_ids.find_one({'name': 'user_ids'}) is None:
            self.users_ids.insert_one({'name': 'user_ids',
                                       'hashes': []})
        self.private_chats = self._db.get_collection(UserQManager.PRIVATE_CHATS)

    def new_request(self, user_id, lang, user_name, profile_pic_id, number_of_chats, chats):
        _hash = str(user_id)+str(datetime.datetime.now())

        new_request = {'user_id': str(user_id), 'lang': lang, 'user_name': user_name,
                       'chats': chats, 'profile_pic_id': profile_pic_id,
                       'number_of_chats': number_of_chats, 'hash': _hash}

        self.users_collection.insert_one(new_request)
        self.users_ids.update_one({'name': 'user_ids'}, {"$push": {'hashes': _hash}})

    def get_user_request_by_hash(self, _hash):
        return self.users_collection.find_one({'hash': _hash})

    def get_users_list(self):
        return self.users_ids.find_one({'name': 'user_ids'})

    def delete_request_by_hash(self, _hash):
        self.users_ids.update_one({'name': 'user_ids'}, {"$pull": {'hashes': _hash}})
        self.users_collection.delete_one({'hash': _hash})

    def init_private_chats(self, chats):
        for chat in chats:
            if chat['private']:
                if self.private_chats.find_one({'chat_id': chat['chat_id']}) is None:
                    self.private_chats.insert_one({'chat_id': chat['chat_id'],
                                                   'chat_title': chat['title'],
                                                   'user_ids': []})
            else:
                self.private_chats.delete_one({'chat_id': chat['chat_id']})

    def add_user_id_to_private_chat(self, user_id, chat_id):
        self.private_chats.update_one({'chat_id': chat_id}, {"$push": {'user_ids': user_id}})

    def remove_user_id_from_private_chat(self, user_id, chat_id):
        # ids = self.private_chats.find_one({'chat_id': chat_id})['user_ids']
        # if user_id in ids:
        #     ids.remove(user_id)

        self.private_chats.update_one({'chat_id': chat_id}, {"$pull": {'user_ids': user_id}})

    def get_private_chat_user_ids(self, chat_id):
        result = self.private_chats.find_one({'chat_id': chat_id})

        if result is not None:
            return result
        else:
            return None




