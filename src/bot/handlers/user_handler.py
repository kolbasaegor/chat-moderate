import copy
from config import SETTINGS
from botforge.api.consts.telegram_bot import ParseMode

ALL_CHATS = [{'chat_id': 123, 'title': 'Test chat 1', 'is_chosen': False, 'link': 'vk.com'},
             {'chat_id': 345, 'title': 'Test chat 2', 'is_chosen': False, 'link': 'yandex.ru'},
             {'chat_id': 678, 'title': 'Test chat 3', 'is_chosen': False, 'link': 'https://t.me/joinchat/mC2rIE70yOZkMTYy'},
             {'chat_id': 109, 'title': 'Test chat 4', 'is_chosen': False, 'link': 'link4'},
             {'chat_id': 78, 'title': 'Test chat 5', 'is_chosen': False, 'link': 'link5'},
             {'chat_id': 456, 'title': 'Test chat 6', 'is_chosen': False, 'link': 'https://t.me/joinchat/z8jjElL10F43NGEy'}]

DISPLAYED_PAGES = SETTINGS['bot']['num_of_displayed_pages']
TOKEN = SETTINGS['bot']['token']
CONCIERGE_ID = SETTINGS['bot']['concierge_id']


class UserHandler:
    @staticmethod
    def get_profile_pic_id(api, user_id):
        user_profile = api.get_user_profile_photos(user_id)
        if len(user_profile.photos) == 0:
            return SETTINGS['bot']['empty_photo']

        file_id = user_profile.photos[0][0].file_id

        return file_id

    @staticmethod
    def get_chosen_chats(session):
        chosen_chats = []
        chosen_chats_ids = session['chosen_chats_ids']
        for chat in ALL_CHATS:
            chat_to_send = copy.deepcopy(chat)
            chat_to_send['is_chosen'] = '🔘'
            if chat_to_send['chat_id'] in chosen_chats_ids:
                chosen_chats.append(chat_to_send)

        return chosen_chats

    @staticmethod
    def render_available_chats(chosen_chats_ids, current_page):
        _from = DISPLAYED_PAGES * current_page
        _to = _from + DISPLAYED_PAGES if _from + DISPLAYED_PAGES < len(ALL_CHATS) else len(ALL_CHATS)

        available_chats_rendered = []

        for chat in ALL_CHATS[_from:_to]:
            chat_params = copy.deepcopy(chat)
            chat_params['is_chosen'] = '🔘' if chat['chat_id'] in chosen_chats_ids else '⚪️'
            chat_params = {k: str(v) for k, v in chat_params.items()}
            available_chats_rendered.append(chat_params)

        return available_chats_rendered

    @staticmethod
    def button_params(current_page):
        max_page_number = len(ALL_CHATS) // DISPLAYED_PAGES - 1
        if len(ALL_CHATS) % DISPLAYED_PAGES != 0:
            max_page_number = max_page_number + 1

        return [{'prev_page': str(current_page),
                 'total': str(max_page_number + 1)},
                {'next_page': str(current_page + 2),
                 'total': str(max_page_number + 1)}]

    @staticmethod
    def send_request_button_params(len_chosen_chats):
        return [{'chats_chosen': str(len_chosen_chats),
                 'total': str(len(ALL_CHATS))}]

    @staticmethod
    def kb_params(session):
        return {'available_chats': UserHandler.render_available_chats(session['chosen_chats_ids'], session['current_page']),
                'buttons': UserHandler.button_params(session['current_page']),
                'send_request_button': UserHandler.send_request_button_params(len(session['chosen_chats_ids']))
                }

    @staticmethod
    def catch_ping(api, view_manager, from_user_id, chat_lang, session):

        if 'chosen_chats_ids' not in session:
            session['chosen_chats_ids'] = []

        message_text = view_manager.get_view('request_chats_access_screen', chat_lang,
                                             screen_params={'total_chats': len(ALL_CHATS)})
        kb = view_manager.get_view('request_chats_access_markup', chat_lang,
                                   markup_params=UserHandler.kb_params(session))

        api.send_message(from_user_id, message_text, reply_markup=kb, parse_mode=ParseMode.html)

    @staticmethod
    def request_access(api, view_manager, from_user_id, from_first_name,
                       from_last_name, chat_lang, callback_query, session, user_requests):
        # TODO: тоже нормально доделать под xml кнопки и тд
        chosen_chats = UserHandler.get_chosen_chats(session)

        if len(chosen_chats) > 0:
            if from_first_name is not None:
                name = from_first_name + " " + from_last_name
            else:
                name = from_first_name

            profile_pic_id = UserHandler.get_profile_pic_id(api, from_user_id)

            user_requests.new_request(from_user_id, chat_lang,
                                      name, profile_pic_id, len(chosen_chats), chosen_chats)

            message = callback_query.message
            current_message_id = message.message_id

            message_text = view_manager.get_view('send_request_screen', chat_lang)
            api.edit_message_text(message_text,
                                  chat_id=from_user_id,
                                  message_id=current_message_id,
                                  parse_mode=ParseMode.html)

            message = "Новый запрос на вступление в чаты"
            kb = view_manager.get_view('concierge_main_menu', chat_lang)
            api.send_message(chat_id=CONCIERGE_ID,
                             text=message,
                             reply_markup=kb)

        else:
            api.send_message(from_user_id, "Вы не выбрали ни одного чата!")

    @staticmethod
    def choose_chat(api, view_manager, chat_lang, callback_query, from_user_id, session):
        api.answer_callback_query(callback_query.id)

        if callback_query is None:
            return

        params = callback_query.data.split('|')[1:]

        if len(params) < 1:
            return

        message = callback_query.message
        current_message_id = message.message_id

        chat_id = int(params[0])

        chosen_chats_ids = session['chosen_chats_ids'] if 'chosen_chats_ids' in session else []

        if chat_id in chosen_chats_ids:
            chosen_chats_ids.remove(chat_id)
        else:
            chosen_chats_ids.append(chat_id)

        session['chosen_chats_ids'] = chosen_chats_ids

        message_text = view_manager.get_view('request_chats_access_screen', chat_lang,
                                             screen_params={'total_chats': len(ALL_CHATS)})
        kb = view_manager.get_view('request_chats_access_markup', chat_lang,
                                   markup_params=UserHandler.kb_params(session))

        api.edit_message_text(message_text,
                              chat_id=from_user_id,
                              message_id=current_message_id,
                              reply_markup=kb,
                              parse_mode=ParseMode.html)

    @staticmethod
    def prev_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        current_page = session['current_page']

        if current_page > 0:
            current_page = current_page - 1
        else:
            # TODO: непустой ответ на дейстиве
            return

        session['current_page'] = current_page

        message = callback_query.message
        current_message_id = message.message_id

        message_text = view_manager.get_view('request_chats_access_screen', chat_lang,
                                             screen_params={'total_chats': len(ALL_CHATS)})
        kb = view_manager.get_view('request_chats_access_markup', chat_lang,
                                   markup_params=UserHandler.kb_params(session))

        api.edit_message_text(message_text,
                              chat_id=from_user_id,
                              message_id=current_message_id,
                              reply_markup=kb,
                              parse_mode=ParseMode.html)

    @staticmethod
    def next_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        current_page = session['current_page']
        max_page_number = len(ALL_CHATS) // DISPLAYED_PAGES - 1
        if len(ALL_CHATS) % DISPLAYED_PAGES != 0:
            max_page_number = max_page_number + 1

        if current_page < max_page_number:
            current_page = current_page + 1
        else:
            # TODO: непустой ответ на дейстиве
            return

        session['current_page'] = current_page

        message = callback_query.message
        current_message_id = message.message_id

        message_text = view_manager.get_view('request_chats_access_screen', chat_lang,
                                             screen_params={'total_chats': len(ALL_CHATS)})
        kb = view_manager.get_view('request_chats_access_markup', chat_lang,
                                   markup_params=UserHandler.kb_params(session))

        api.edit_message_text(message_text,
                              chat_id=from_user_id,
                              message_id=current_message_id,
                              reply_markup=kb,
                              parse_mode=ParseMode.html)
