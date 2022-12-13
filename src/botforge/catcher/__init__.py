from typing import NewType

from botforge.catcher.match import MatchType


class Catcher(object):
    """
    Router.
    Catches all the requests from end users and dispatches them.
    """
    def __init__(self):
        self.catches = []
        self.hooks = []
        self.events = []
        self.intents = []

    @staticmethod
    def pack_handler(func, match):
        return {'func': func,
                'match': match,
                'func_name': func.__name__,
                'wanted_arguments': func.__code__.co_varnames[:func.__code__.co_argcount]}

    def catch(self, match: MatchType):
        def decorator(func):
            self.catches.append(Catcher.pack_handler(func, match))

            return func

        return decorator

    def hook(self, match: MatchType):
        def decorator(func):
            self.hooks.append(Catcher.pack_handler(func, match))

            return func

        return decorator

    def event(self, match: MatchType):
        # TODO: change the signature

        def decorator(func):
            self.events.append(Catcher.pack_handler(func, match))

            return func

        return decorator

    def intent(self, match: MatchType):
        def decorator(func):
            self.intents.append(Catcher.pack_handler(func, match))

            return func

        return decorator

    @staticmethod
    def execute(handler, arguments_dict):
        func, wanted_arguments = handler['func'], handler['wanted_arguments']

        if wanted_arguments is None:
            return func()

        return func(**{key: value for key, value in arguments_dict.items() if key in wanted_arguments})

    def try_catch(self, updates, argument_resolvers):
        for update in updates:
            for x in self.catches:
                if x['match'].matches(update, argument_resolvers=argument_resolvers):
                    self.execute(x, argument_resolvers)
                    break

    def try_hook(self, updates, argument_resolvers):
        for update in updates:
            for x in self.hooks:
                if x['match'].matches(update, argument_resolvers=argument_resolvers):
                    self.execute(x, argument_resolvers)

    def get_tree_intent_handler(self, intent_type: str, tree_id: str, state_id: str):
        for intent in self.intents:
            intent_match = intent['match']

            if intent_match.intent_type == intent_type:
                if intent_match.tree_id == tree_id \
                        and intent_match.state_id == state_id:
                    return intent

        return None

    def get_tree_event_handler(self, event_type: str, tree_id: str, state_id: str):
        for event in self.events:
            event_match = event['match']

            if event_match.event_type == event_type:
                if event_match.tree_id == tree_id \
                        and event_match.state_id == state_id:
                    return event

        return None


CatcherType = NewType('Catcher', Catcher)
