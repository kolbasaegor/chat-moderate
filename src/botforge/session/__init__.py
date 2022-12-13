import datetime
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


class SessionManager(object):
    SESSIONS_COLLECTION = 'sessions'
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
            print('Connected to MongoDB')

        self._db = client.get_database(config['db']['name'])
        self._sessions_collection = self._db.get_collection(SessionManager.SESSIONS_COLLECTION)

    @staticmethod
    def new_session(user_id, lang, state, tree_id, state_id, initial_page):
        return {'user_id': str(user_id), 'lang': lang, 'state': state, 'created_at': datetime.datetime.now(),
                'tree_id': tree_id, 'state_id': state_id, 'current_page': initial_page}

    def get_user_session(self, user_id):
        # TODO: introduce mutex for enabling concurrency?
        # NOTE: reference to a user session gets passed all around, so there must be a mutex or something when
        #  writing to a session object
        # looking for a session whose user_id is whether str or int
        search_filter = {'$or': [{'user_id': str(user_id)}]}

        if isinstance(user_id, int):
            search_filter['$or'].append({'user_id': user_id})
        elif isinstance(user_id, str) and user_id.isdigit():
            search_filter['$or'].append({'user_id': int(user_id)})

        session_dict = self._sessions_collection.find_one(search_filter)

        if session_dict is not None:
            return session_dict

        session_dict = SessionManager.new_session(user_id,
                                                  self._config['session_manager']['default_lang'],
                                                  self._config['session_manager']['default_state'],
                                                  self._config['session_manager']['default_tree_id'],
                                                  self._config['session_manager']['default_state_id'],
                                                  self._config['session_manager']['default_page'])
        self.update_user_session(session_dict)

        return session_dict

    def update_user_session(self, session_dict):
        session_mongo_id = session_dict.get('_id')

        if 'user_id' in session_dict:
            session_dict['user_id'] = str(session_dict['user_id'])

        session_dict['updated_at'] = datetime.datetime.now()

        if session_mongo_id is not None:
            self._sessions_collection.update_one({'_id': session_dict['_id']}, {'$set': session_dict})
        else:
            self._sessions_collection.insert_one(session_dict)
