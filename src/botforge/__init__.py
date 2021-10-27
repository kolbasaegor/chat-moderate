import os
import sys
from time import sleep

from botforge.api.methods.telegram_bot import TelegramBotProxy
from botforge.api.objects.telegram_bot import Update, Message, User, Chat
from botforge.catcher import CatcherType, Catcher
from botforge.forms import Forms
from botforge.l10n import L10n
from botforge.module_manager import ModuleManager
from botforge.session import SessionManager
from botforge.users_queue import UserQManager
from botforge.trees import Trees
from botforge.utils import import_module, get_directories_names, escape_html
from botforge.view_manager import ViewManager


class Bot(object):
    path_modules = './modules'
    path_l10n = './l10n'
    path_views = './views'

    #

    class Extract:
        @staticmethod
        def from_user_id(update: Update):
            if update is None:
                return None

            if update.message is not None and update.message.from_user is not None:
                return update.message.from_user.id

            if update.callback_query is not None and update.callback_query.from_user is not None:
                return update.callback_query.from_user.id

            return None

        @staticmethod
        def from_chat_id(update: Update):
            if update is None:
                return None

            if update.message is not None and update.message.chat is not None:
                return update.message.chat.id

            return None

        @staticmethod
        def message_text(update: Update):
            if update is None:
                return None

            if update.message is not None:
                return update.message.text

            return None

        @staticmethod
        def from_username(update: Update):
            if update is None:
                return None

            if update.message is not None:
                return update.message.chat.username

            if update.callback_query is not None and update.callback_query.from_user is not None:
                return update.callback_query.from_user.username

            return None

        @staticmethod
        def from_first_name(update: Update):

            if update.message is not None and update.message.from_user is not None:
                return update.message.from_user.first_name

            if update.callback_query is not None and update.callback_query.from_user is not None:
                return update.callback_query.from_user.first_name

            return None

        @staticmethod
        def from_last_name(update: Update):

            if update.message is not None and update.message.from_user is not None:
                return update.message.from_user.last_name

            if update.callback_query is not None and update.callback_query.from_user is not None:
                return update.callback_query.from_user.last_name

            return None

        @staticmethod
        def start_query(update):
            if update is None:
                return None

            if update.message is None or update.message.text is None:
                return None

            message_text = update.message.text

            if message_text.startswith('/start') and len(message_text) >= 8:
                return message_text[8:]

            return None

    def __init__(self, token: str,
                 catcher: Catcher = None, argument_resolvers: dict = None,
                 config: dict = None, mount_modules=True):
        self.modules = self._load_modules()
        self.config = config
        self._preset_argument_resolvers = argument_resolvers if argument_resolvers is not None and len(
            argument_resolvers.keys()) > 0 else dict()

        self.catcher = catcher if catcher is not None else Catcher()
        self.api = TelegramBotProxy(bot_token=token)
        self.l10n = L10n(modules=self.modules)
        self.view_manager = ViewManager(modules=self.modules, l10n=self.l10n)
        self.session_manager = SessionManager(config)
        self.users_q_manager = UserQManager(config)

        self.last_update_id = 0

        if mount_modules:
            self.mount_modules(self.modules)

    @staticmethod
    def _load_modules():
        # TODO: parse dependencies from "./package.json"
        module_authors = get_directories_names(Bot.path_modules)
        modules = dict()

        # first of all, let's load root module
        modules['.'] = ModuleManager.load_module(os.path.abspath('./'))

        for author in module_authors:
            author_modules_path = os.path.join(Bot.path_modules, author)

            author_modules = get_directories_names(author_modules_path)

            for module in author_modules:
                module_versions_path = os.path.join(author_modules_path, module)

                module_versions = get_directories_names(module_versions_path)

                for version in module_versions:
                    versioned_module_path = os.path.join(author, module, version)

                    full_module_path = os.path.join(Bot.path_modules, versioned_module_path)
                    abs_module_path = os.path.abspath(full_module_path)

                    # make the module importable
                    sys.path.insert(0, abs_module_path)

                    modules[versioned_module_path] = ModuleManager.load_module(abs_module_path)

        # TODO: make sure modules dependencies are satisfied

        return modules

    def mount_modules(self, modules: dict):
        for module_name in modules.keys():
            modules[module_name]['content'].mount(self)

    def add_argument_resolver(self, name, resolver):
        if name in self._preset_argument_resolvers.keys():
            print('Warning: argument resolver "%s" has been overwritten' % name)

        self._preset_argument_resolvers[name] = resolver

    def get_argument_resolvers(self, update):
        # TODO: pull argument provider out of arguments dict
        # TODO: make all possible properties lazy?(overwrite __call__ ?)
        argument_resolvers = {'update': update,
                              'message': update.message,
                              'inline_query': update.inline_query,
                              'callback_query': update.callback_query,
                              'chosen_inline_result': update.chosen_inline_result,
                              'edited_message': update.edited_message,
                              'api': self.api,
                              'from_user_id': self.Extract.from_user_id(update),
                              'from_chat_id': self.Extract.from_chat_id(update),
                              'from_username': self.Extract.from_username(update),
                              'from_first_name': self.Extract.from_first_name(update),
                              'from_last_name': self.Extract.from_last_name(update),
                              'message_text': self.Extract.message_text(update),
                              'escaped_message_text': escape_html(self.Extract.message_text(update)),
                              'start_query': self.Extract.start_query(update),
                              'view_manager': self.view_manager,
                              'catcher': self.catcher,
                              'user_requests': self.users_q_manager
                              }

        argument_resolvers['session'] = self.session_manager.get_user_session(argument_resolvers['from_user_id'])

        argument_resolvers['chat_lang'] = argument_resolvers['session'].get('lang')
        argument_resolvers['_'] = self.l10n.translator(argument_resolvers['chat_lang'])
        argument_resolvers['forms'] = Forms(self.api, self.session_manager, argument_resolvers['session'], self.view_manager)
        argument_resolvers['trees'] = Trees(self.view_manager, argument_resolvers['session'],
                                            self.catcher, argument_resolvers)
        argument_resolvers['last_message_id'] = argument_resolvers['session'].get('last_message_id')

        if self._preset_argument_resolvers is not None:
            for argument_resolver in self._preset_argument_resolvers.keys():
                if argument_resolver in argument_resolvers:
                    print('Warning: argument resolver "%s" has been overwritten' % argument_resolver)

            argument_resolvers.update(self._preset_argument_resolvers)

        return argument_resolvers

    def loop(self):
        while True:
            updates = self.api.get_updates(offset=(self.last_update_id + 1))

            for update in updates:
                argument_resolvers = self.get_argument_resolvers(update)
                updates_to_try = [update]

                self.catcher.try_hook(updates_to_try, argument_resolvers)
                self.catcher.try_catch(updates_to_try, argument_resolvers)

                session = argument_resolvers.get('session')

                if session is not None:
                    self.session_manager.update_user_session(session)

                if update.update_id > self.last_update_id:
                    self.last_update_id = update.update_id

            sleep(0.1)
