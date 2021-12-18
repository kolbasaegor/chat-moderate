import copy
import datetime

from config import SETTINGS
from botforge.api.consts.telegram_bot import ParseMode
import from_google_table

ALL_CHATS = from_google_table.get_table()
LAST_UPDATE = datetime.datetime(1970, 1, 1, 1, 1, 1)

DISPLAYED_PAGES = SETTINGS['bot']['num_of_displayed_pages']
TOKEN = SETTINGS['bot']['token']
CONCIERGE_ID = SETTINGS['bot']['concierge_id']
INTERVAL = SETTINGS['bot']['interval']
UPDATE_TIME = SETTINGS['google']['update_time']


class UserHandler:
    @staticmethod
    def update_chats(api, user_requests):
        global ALL_CHATS

        chats_from_google_table = from_google_table.get_table()
        if chats_from_google_table:
            ALL_CHATS = chats_from_google_table
            user_requests.init_private_chats(ALL_CHATS)
            api.send_message(chat_id=CONCIERGE_ID,
                             text='Чаты успешно обновлены')
        else:
            api.send_message(chat_id=CONCIERGE_ID,
                             text='Что-то пошло не так при загрузке чатов из таблицы.')

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
    def button_params(current_page, max_page_number):
        if current_page == 0:
            return [{'next_page': str(current_page + 2),
                     'total': str(max_page_number + 1)}]
        elif current_page == max_page_number:
            return [{'prev_page': str(current_page),
                     'total': str(max_page_number + 1)}]
        else:
            return [{'prev_page': str(current_page),
                     'total': str(max_page_number + 1)},
                    {'next_page': str(current_page + 2),
                     'total': str(max_page_number + 1)}]

    @staticmethod
    def send_request_button_params(len_chosen_chats):
        return [{'chats_chosen': str(len_chosen_chats),
                 'total': str(len(ALL_CHATS))}]

    @staticmethod
    def get_max_page_number():
        max_page_number = len(ALL_CHATS) // DISPLAYED_PAGES - 1
        if len(ALL_CHATS) % DISPLAYED_PAGES != 0:
            max_page_number = max_page_number + 1

        return max_page_number

    @staticmethod
    def kb_params(session, view_manager, chat_lang):
        max_page_number = UserHandler.get_max_page_number()
        current_page = session['current_page']
        chosen_chats_ids = session['chosen_chats_ids']

        params = {
            'available_chats': UserHandler.render_available_chats(chosen_chats_ids,
                                                                  current_page),
            'buttons': UserHandler.button_params(current_page, max_page_number),
            'send_request_button': UserHandler.send_request_button_params(len(chosen_chats_ids))
        }

        if max_page_number == 0:
            kb = view_manager.get_view('one_page_markup', chat_lang,
                                       markup_params=params)
        elif current_page == 0:
            kb = view_manager.get_view('only_right_button_markup', chat_lang,
                                       markup_params=params)
        elif current_page == max_page_number:
            kb = view_manager.get_view('only_left_button_markup', chat_lang,
                                       markup_params=params)
        else:
            kb = view_manager.get_view('request_chats_access_markup', chat_lang,
                                       markup_params=params)

        return kb

    @staticmethod
    def catch_ping(api, view_manager, from_user_id, chat_lang, session, user_requests):
        global LAST_UPDATE
        if (datetime.datetime.now() - LAST_UPDATE).seconds > UPDATE_TIME:
            UserHandler.update_chats(api, user_requests)
            LAST_UPDATE = datetime.datetime.now()

        session['chosen_chats_ids'] = []

        message_text = view_manager.get_view('request_chats_access_screen', chat_lang,
                                             screen_params={'total_chats': len(ALL_CHATS)})

        kb = UserHandler.kb_params(session, view_manager, chat_lang)

        api.send_message(from_user_id, message_text, reply_markup=kb, parse_mode=ParseMode.html)

    @staticmethod
    def request_access(api, view_manager, from_user_id, from_first_name,
                       from_last_name, chat_lang, callback_query, session, user_requests):

        chosen_chats = UserHandler.get_chosen_chats(session)

        if 'last_request_time' in session:
            if (datetime.datetime.now() - session['last_request_time']).seconds < INTERVAL:
                if session['lang'] == 'ru':
                    msg = "Слишком много запросов. Подождите, пожалуйста"
                else:
                    msg = "Too many requests. Please wait"
                api.send_message(from_user_id, msg)
                return

        if len(chosen_chats) > 0:
            if from_last_name is not None:
                name = from_first_name + " " + from_last_name
            else:
                name = from_first_name

            profile_pic_id = UserHandler.get_profile_pic_id(api, from_user_id)

            user_requests.new_request(from_user_id, chat_lang,
                                      name, profile_pic_id, len(chosen_chats), chosen_chats)

            session['last_request_time'] = datetime.datetime.now()

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
        kb = UserHandler.kb_params(session, view_manager, chat_lang)

        api.edit_message_text(message_text,
                              chat_id=from_user_id,
                              message_id=current_message_id,
                              reply_markup=kb,
                              parse_mode=ParseMode.html)

    @staticmethod
    def invert_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        message = callback_query.message
        current_message_id = message.message_id

        chosen_chats_ids = session['chosen_chats_ids'] if 'chosen_chats_ids' in session else []
        current_page = session['current_page']

        _from = DISPLAYED_PAGES * current_page
        _to = _from + DISPLAYED_PAGES if _from + DISPLAYED_PAGES < len(ALL_CHATS) else len(ALL_CHATS)

        for chat in ALL_CHATS[_from:_to]:
            chat_params = copy.deepcopy(chat)
            if chat_params['chat_id'] in chosen_chats_ids:
                chosen_chats_ids.remove(chat_params['chat_id'])
            else:
                chosen_chats_ids.append(chat_params['chat_id'])

        session['chosen_chats_ids'] = chosen_chats_ids

        message_text = view_manager.get_view('request_chats_access_screen', chat_lang,
                                             screen_params={'total_chats': len(ALL_CHATS)})
        kb = UserHandler.kb_params(session, view_manager, chat_lang)

        api.edit_message_text(message_text,
                              chat_id=from_user_id,
                              message_id=current_message_id,
                              reply_markup=kb,
                              parse_mode=ParseMode.html)

    @staticmethod
    def prev_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        current_page = session['current_page']

        current_page = current_page - 1

        session['current_page'] = current_page

        message = callback_query.message
        current_message_id = message.message_id

        message_text = view_manager.get_view('request_chats_access_screen', chat_lang,
                                             screen_params={'total_chats': len(ALL_CHATS)})
        kb = UserHandler.kb_params(session, view_manager, chat_lang)

        api.edit_message_text(message_text,
                              chat_id=from_user_id,
                              message_id=current_message_id,
                              reply_markup=kb,
                              parse_mode=ParseMode.html)

    @staticmethod
    def next_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        current_page = session['current_page']

        current_page = current_page + 1

        session['current_page'] = current_page

        message = callback_query.message
        current_message_id = message.message_id

        message_text = view_manager.get_view('request_chats_access_screen', chat_lang,
                                             screen_params={'total_chats': len(ALL_CHATS)})
        kb = UserHandler.kb_params(session, view_manager, chat_lang)

        api.edit_message_text(message_text,
                              chat_id=from_user_id,
                              message_id=current_message_id,
                              reply_markup=kb,
                              parse_mode=ParseMode.html)
