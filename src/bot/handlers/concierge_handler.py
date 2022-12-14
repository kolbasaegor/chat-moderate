import copy
import time
import threading

from config import SETTINGS
from handlers.user_handler import DISPLAYED_PAGES
from botforge.api.consts.telegram_bot import ParseMode
from botforge.api.objects.telegram_bot import InlineKeyboardMarkup, InlineKeyboardButton

EXPIRE = SETTINGS['bot']['expire_days'] * 24 * 60 * 60
MEMBER_LIMIT = SETTINGS['bot']['member_limit']


class ConciergeHandler:
    @staticmethod
    def switch_lang(session):
        if session['lang'] == 'en':
            session['lang'] = 'ru'
        else:
            session['lang'] = 'en'

    @staticmethod
    def catch_ping(api, view_manager, from_user_id, chat_lang, user_requests):
        unreviewed_chats_num = len(user_requests.get_users_list()['hashes'])

        if unreviewed_chats_num == 0:
            message_text = "No new chat requests"
            api.send_message(from_user_id, message_text)
            return

        message_text = "You have " + str(unreviewed_chats_num) + " pending requests to join chats"
        kb = view_manager.get_view('concierge_main_menu', chat_lang,
                                   )

        api.send_message(from_user_id, message_text, reply_markup=kb, parse_mode=ParseMode.html)

    @staticmethod
    def show_first_request(api, view_manager, from_user_id, chat_lang, user_requests, session):
        if len(user_requests.get_users_list()['hashes']) == 0:
            return

        first_user_hash = user_requests.get_users_list()['hashes'][0]

        chosen_chats_ids = []
        user = user_requests.get_user_request_by_hash(first_user_hash)

        session['CHATS'] = user['chats']
        session['USERNAME'] = user['user_name']
        session['USER_ID'] = user['user_id']

        CHATS = session['CHATS']
        username = session['USERNAME']
        profile_pic_id = user['profile_pic_id']

        session['current_page'] = 0

        for chat in CHATS:
            if chat['is_chosen'] == '🔘':
                chosen_chats_ids.append(chat['chat_id'])
        session['chosen_chats_ids'] = chosen_chats_ids

        message_text = ("New request to access chats:\n\n" +
                        "User: " + username + "\n\n" +
                        "Requested chats (Total " + str(len(CHATS)) + ")," +
                        "Check allowed:")

        kb = ConciergeHandler.kb_params(session, view_manager, chat_lang)

        api.send_photo(chat_id=from_user_id,
                       photo=profile_pic_id,
                       caption=message_text,
                       reply_markup=kb
                       )

    @staticmethod
    def get_chosen_chats(session):
        CHATS = session['CHATS']

        chosen_chats = []
        chosen_chats_ids = session['chosen_chats_ids']
        for chat in CHATS:
            chat_to_send = copy.deepcopy(chat)
            chat_to_send['is_chosen'] = '🔘'
            if chat_to_send['chat_id'] in chosen_chats_ids:
                chosen_chats.append(chat_to_send)

        return chosen_chats

    @staticmethod
    def render_available_chats(chosen_chats_ids, current_page, session):
        CHATS = session['CHATS']
        _from = DISPLAYED_PAGES * current_page
        _to = _from + DISPLAYED_PAGES if _from + DISPLAYED_PAGES < len(CHATS) else len(CHATS)

        available_chats_rendered = []

        for chat in CHATS[_from:_to]:
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
    def send_response_button_params(len_chosen_chats, session):
        CHATS = session['CHATS']
        return [{'chats_chosen': str(len_chosen_chats),
                 'total': str(len(CHATS))}]

    @staticmethod
    def response_kb_markup(chats):
        reply_markup = []
        for chat in chats:
            reply_markup.append([
                InlineKeyboardButton(text=chat['title'], url=chat['link'])
            ])

        return InlineKeyboardMarkup(reply_markup)

    @staticmethod
    def get_max_page_number(session):
        CHATS = session['CHATS']
        max_page_number = len(CHATS) // DISPLAYED_PAGES - 1
        if len(CHATS) % DISPLAYED_PAGES != 0:
            max_page_number = max_page_number + 1

        return max_page_number

    @staticmethod
    def kb_params(session, view_manager, chat_lang):
        max_page_number = ConciergeHandler.get_max_page_number(session)
        current_page = session['current_page']
        chosen_chats_ids = session['chosen_chats_ids']

        params = {
            'available_chats': ConciergeHandler.render_available_chats(chosen_chats_ids,
                                                                       current_page, session),
            'buttons': ConciergeHandler.button_params(current_page, max_page_number),
            'response': ConciergeHandler.send_response_button_params(len(chosen_chats_ids), session)
        }

        if max_page_number == 0:
            kb = view_manager.get_view('concierge_one_page_markup', chat_lang,
                                       markup_params=params)
        elif current_page == 0:
            kb = view_manager.get_view('concierge_only_right_button_markup', chat_lang,
                                       markup_params=params)
        elif current_page == max_page_number:
            kb = view_manager.get_view('concierge_only_left_button_markup', chat_lang,
                                       markup_params=params)
        else:
            kb = view_manager.get_view('concierge_chats_markup', chat_lang,
                                       markup_params=params)

        return kb

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

        CHATS = session['CHATS']
        username = session['USERNAME']

        chosen_chats_ids = session['chosen_chats_ids'] if 'chosen_chats_ids' in session else []

        if chat_id in chosen_chats_ids:
            chosen_chats_ids.remove(chat_id)
        else:
            chosen_chats_ids.append(chat_id)

        session['chosen_chats_ids'] = chosen_chats_ids

        message_text = ("New request to access chats:\n\n" +
                        "User: " + username + "\n\n" +
                        "Requested chats (Total " + str(len(CHATS)) + ")," +
                        "Check allowed:")
        kb = ConciergeHandler.kb_params(session, view_manager, chat_lang)

        api.edit_message_caption(caption=message_text,
                                 chat_id=from_user_id,
                                 message_id=current_message_id,
                                 reply_markup=kb)

    @staticmethod
    def prev_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        current_page = session['current_page']

        current_page = current_page - 1

        session['current_page'] = current_page

        message = callback_query.message
        current_message_id = message.message_id

        CHATS = session['CHATS']
        username = session['USERNAME']

        message_text = ("New request to access chats:\n\n" +
                        "User: " + username + "\n\n" +
                        "Requested chats (Total " + str(len(CHATS)) + ")," +
                        "Check allowed:")
        kb = ConciergeHandler.kb_params(session, view_manager, chat_lang)

        api.edit_message_caption(caption=message_text,
                                 chat_id=from_user_id,
                                 message_id=current_message_id,
                                 reply_markup=kb)

    @staticmethod
    def next_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        current_page = session['current_page']
        CHATS = session['CHATS']
        username = session['USERNAME']

        current_page = current_page + 1

        session['current_page'] = current_page

        message = callback_query.message
        current_message_id = message.message_id

        message_text = ("New request to access chats:\n\n" +
                        "User: " + username + "\n\n" +
                        "Requested chats (Total " + str(len(CHATS)) + ")," +
                        "Check allowed:")
        kb = ConciergeHandler.kb_params(session, view_manager, chat_lang)

        api.edit_message_caption(caption=message_text,
                                 chat_id=from_user_id,
                                 message_id=current_message_id,
                                 reply_markup=kb)

    @staticmethod
    def send_response(api, view_manager, chat_lang, from_user_id, session, user_requests):
        first_user_hash = user_requests.get_users_list()['hashes'][0]
        approved_chats = ConciergeHandler.get_chosen_chats(session)
        unreviewed_chats_num = len(user_requests.get_users_list()['hashes'])

        if len(approved_chats) == 0:
            ConciergeHandler.reject_request(api, view_manager, chat_lang,
                                            from_user_id, user_requests, session)
            return

        ConciergeHandler.send_links_to_user(api, approved_chats, user_requests, session)

        CHATS = session['CHATS']
        username = session['USERNAME']

        message_text = "User " + username + " received a response\nto a request to join chats (access in " \
                       + str(len(approved_chats)) + " из " + str(len(CHATS)) + ")"
        dope = "\n\nYou have left " + str(unreviewed_chats_num) + " pending requests"
        zero_requests = "\n\nNo new requests :)"

        kb = view_manager.get_view('concierge_main_menu', chat_lang)

        if unreviewed_chats_num - 1 > 0:
            api.send_message(text=message_text + dope,
                             chat_id=from_user_id,
                             reply_markup=kb,
                             )
        else:
            api.send_message(text=message_text + zero_requests,
                             chat_id=from_user_id,
                             )

        user_requests.delete_request_by_hash(first_user_hash)

    @staticmethod
    def reject_request(api, view_manager, chat_lang, from_user_id, user_requests, session):
        first_user_hash = user_requests.get_users_list()['hashes'][0]
        unreviewed_chats_num = len(user_requests.get_users_list()['hashes'])

        username = session['USERNAME']
        USER_ID = session['USER_ID']

        api.send_message(USER_ID, "Your request to join chats has been denied")

        message_text = "User " + username + "did not\naccess any of the chats"

        dope = "\n\nYou have left " + str(unreviewed_chats_num) + " pending requests"

        zero_requests = "\n\nNo new requests :)"

        kb = view_manager.get_view('concierge_main_menu', chat_lang)

        if unreviewed_chats_num - 1 > 0:
            api.send_message(text=message_text + dope,
                             chat_id=from_user_id,
                             reply_markup=kb,
                             )
        else:
            api.send_message(text=message_text + zero_requests,
                             chat_id=from_user_id,
                             )

        user_requests.delete_request_by_hash(first_user_hash)

    @staticmethod
    def send_links_to_user(api, approved_chats, user_requests, session):
        thread = LinkCreator(api, approved_chats, user_requests, session)
        thread.start()


class LinkCreator(threading.Thread):
    def __init__(self, api, approved_chats, user_requests, session):
        threading.Thread.__init__(self)
        self.api = api
        self.approved_chats = approved_chats
        self.user_requests = user_requests
        self.session = session

    def run(self):
        CHATS = self.session['CHATS']
        USER_ID = self.session['USER_ID']

        if self.session['lang'] == 'ru':
            msg = "Одобрен доступ к " + str(len(self.approved_chats)) + " чатам из " + str(
                len(CHATS)) + " запрошенных:\n\n"
        else:
            msg = "Approved access to " + str(len(self.approved_chats)) + " chats out of " + str(
                len(CHATS)) + " requested:\n\n"

        current_time = int(time.time())
        chats_to_send = []
        for chat in self.approved_chats:
            time.sleep(SETTINGS['bot']['delay'])
            if chat['private']:
                self.user_requests.add_user_id_to_private_chat(USER_ID, chat['chat_id'])

            link = self.api.create_chat_invite_link(chat_id=chat['chat_id'],
                                                    expire_date=current_time + EXPIRE,
                                                    member_limit=MEMBER_LIMIT)
            if link is not None:
                chat['link'] = link
                chat['chat_id'] = str(chat['chat_id'])
                chats_to_send.append(chat)

                msg += "  • " + chat['title'] + "\n"

        if self.session['lang'] == 'ru':
            msg += "\nДля вступления в чаты используйте кнопки:"
        else:
            msg += "\nTo enter chats, use the buttons:"

        self.api.send_message(chat_id=USER_ID,
                              text=msg,
                              reply_markup=ConciergeHandler.response_kb_markup(chats_to_send))
