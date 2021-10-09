from abc import abstractmethod
from typing import Dict, Any

from botforge import Update, Trees
from botforge.catcher.match import Match
from botforge.view_manager import MarkupManager


# telegram
#  basic types


class TelegramUpdateMatches(Match):
    @abstractmethod
    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        return Match.matches(self, update)


# extension on updates match


class MessageText(TelegramUpdateMatches):
    def __init__(self, text: str):
        self._text = text

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        has_text = not (update is None or update.message is None or update.message.text is None)

        if not has_text:
            return False

        return update.message.text == self._text


class MessageTextNotEmpty(TelegramUpdateMatches):
    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        has_text = not (update is None or update.message is None or update.message.text is None)

        return has_text


class EmptyMessageText(TelegramUpdateMatches):
    def __init__(self):
        pass

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs):
        has_text = not (update is None or update.message is None or update.message.text is None)

        return not has_text


class Voice(TelegramUpdateMatches):
    def __init__(self):
        pass

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs):
        has_voice = not (update is None or update.message is None or update.message.voice is None)

        return has_voice


class Command(TelegramUpdateMatches):
    def __init__(self, command: str):
        self._command = command

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        has_text = not (update is None or update.message is None or update.message.text is None)

        if not has_text:
            return False

        return update.message.text.startswith('/%s' % self._command)


class CallbackQuery(TelegramUpdateMatches):
    def __init__(self, callback_data: str):
        self._data = callback_data

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        has_data = not (update is None or update.callback_query is None or update.callback_query.data is None)

        if not has_data:
            return False

        return update.callback_query.data.startswith(self._data)


class MarkupButtonClicked(TelegramUpdateMatches):
    def __init__(self, data: str):
        self._data = data

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        button_type = 'text' if update.message is not None and update.message.text is not None else \
            ('inline' if not
            (update is None or update.callback_query is None or update.callback_query.data is None) else 'none')

        if button_type == 'text':
            message_text = update.message.text

            translator = argument_resolvers.get('_')

            if translator is None:
                # can't check - no translator set
                return False

            # TODO: add check with "resolve_button_arguments"
            # TODO: put recognized args of the button into argument_resolvers
            expected_text = translator(self._data)

            if message_text == expected_text:
                # got 100% match
                return True

            # gonna check against buttons & their masks

            view_manager = argument_resolvers.get('view_manager')

            if view_manager is None:
                # can't check - no view manager set
                return False

            return MarkupManager.text_matches_btn(view_manager.get_markup_views(), message_text, self._data)
        elif button_type == 'inline':
            return update.callback_query.data.startswith(self._data)

        return False


class PhotoContent(TelegramUpdateMatches):
    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        if update.message is None or update.message.photo is None:
            return False

        return True


class SessionField(TelegramUpdateMatches):
    def __init__(self, field: str, value: Any):
        self._field = field
        self._value = value

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        session = argument_resolvers.get('session')

        if session is None:
            print('Warning: no session provided', flush=True)
            return False

        return session.get(self._field) == self._value


class SessionState(SessionField):
    def __init__(self, value: Any):
        super().__init__('state', value)

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        return super().matches(update, argument_resolvers)


class NewChatMember(TelegramUpdateMatches):
    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        member_joined = not (update is None or update.message is None or update.message.new_chat_member is None)

        return member_joined


class LeftChatMember(TelegramUpdateMatches):
    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        member_left = not (update is None or update.message is None or update.message.left_chat_member is None)

        return member_left


class InTree(TelegramUpdateMatches):
    def __init__(self, tree_id: str):
        self._tree_id = tree_id

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        session = argument_resolvers.get('session')

        if session is None:
            print('Warning: no session provided', flush=True)
            return False

        return session.get('tree_id') == self._tree_id


class InTreeState(TelegramUpdateMatches):
    def __init__(self, tree_id: str, state_id: Any):
        self._tree_id = tree_id
        self._state_id = state_id

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        session = argument_resolvers.get('session')

        if session is None:
            print('Warning: no session provided', flush=True)
            return False

        return session.get('tree_id') == self._tree_id and session.get('state_id') == self._state_id


# trees
#  basic types


class BasicTreeMatches(TelegramUpdateMatches):
    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        return super().matches(update, argument_resolvers)


class BasicTreeEventMatches(BasicTreeMatches):
    def __init__(self, event_type: str, tree_id: str, state_id: str):
        self.event_type = event_type
        self.tree_id = tree_id
        self.state_id = state_id

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], **kwargs) -> bool:
        return False


class BasicTreeIntentMatches(BasicTreeMatches):
    def __init__(self, intent_type: str, tree_id: str, state_id: str):
        self.intent_type = intent_type
        self.tree_id = tree_id
        self.state_id = state_id

    def matches(self, update: Update, argument_resolvers: Dict[Any, Any], *args, **kwargs) -> bool:
        return False


# intents


class GetStateEntryParams(BasicTreeIntentMatches):
    def __init__(self, tree_id: str, state_id: str):
        super().__init__(Trees.Intents.get_state_entry_params, tree_id, state_id)


# events

class OnStateEntered(BasicTreeEventMatches):
    def __init__(self, tree_id: str, state_id: str):
        super().__init__(Trees.Events.on_state_entered, tree_id, state_id)


class OnStateLeft(BasicTreeEventMatches):
    def __init__(self, tree_id: str, state_id: str):
        super().__init__(Trees.Events.on_state_left, tree_id, state_id)


class OnStateRepeated(BasicTreeEventMatches):
    def __init__(self, tree_id: str, state_id: str):
        super().__init__(Trees.Events.on_state_repeated, tree_id, state_id)
