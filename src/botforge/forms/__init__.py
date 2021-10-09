import time

from botforge.api.consts.telegram_bot import ParseMode


class Forms:
    """
    Forms.
    Aware of current user session
    """
    MAX_MESSAGE_LENGTH = 4096

    def __init__(self, api, session_manager, user_session, view_manager):
        self._api = api
        self._session_manager = session_manager
        self._user_session = user_session
        self._view_manager = view_manager

    def send_form(self, user_id: str, form_id: str, form_params: dict, l10n_params: dict, save_message_id=True, **kwargs):
        lang = self._user_session['lang']

        form = self._view_manager.get_form(form_id, lang, form_params, l10n_params)

        if form is None:
            print('Warning: could not get form with id = %s' % form_id)
            return False

        message = form['message']

        screen_text = message.get('screen')
        markup = message.get('markup')

        if len(screen_text) > Forms.MAX_MESSAGE_LENGTH:
            print('Error: message is too long - %s; skipped' % len(screen_text), flush=True)
            return False

        last_message_id = self._user_session.get('last_message_id')

        if last_message_id is not None:
            try:
                # remove reply markup of the last message
                self._api.edit_message_reply_markup(chat_id=user_id, message_id=last_message_id)
            except Exception as e:
                pass

        message = self._api.send_message(user_id, text=screen_text, reply_markup=markup, parse_mode=ParseMode.html)

        if save_message_id:
            message_id = None

            try:
                message_id = message.message_id
            except:
                print('Error: could not get id of the message that has been sent')

            self._user_session['last_message_id'] = message_id

        return True

    def update_form(self, user_id: str, message_id: str, form_id: str, form_params: dict, l10_params: dict, **kwargs):
        lang = self._user_session['lang']

        form = self._view_manager.get_form(form_id, lang, form_params, l10_params)

        if form is None:
            print('Warning: could not get form with id = %s' % form_id)
            return False

        message = form['message']

        screen_text = message.get('screen')
        markup = message.get('markup')

        if len(screen_text) > Forms.MAX_MESSAGE_LENGTH:
            print('Error: message is too long - %s; skipped' % len(screen_text), flush=True)
            return False

        self._api.edit_message_text(chat_id=user_id, text=screen_text, message_id=message_id,
                                    reply_markup=markup, parse_mode=ParseMode.html)

        return True

