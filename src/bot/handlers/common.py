from config import SETTINGS
from botforge.catcher.match import Any
from botforge.matches import Command, MarkupButtonClicked, NewChatMember

from handlers.user_handler import UserHandler as usr
from handlers.concierge_handler import ConciergeHandler as con

CONCIERGE_ID = SETTINGS['bot']['concierge_id']


def mount(bot):
    @bot.catcher.catch(
        Any(
            NewChatMember()
        )
    )
    def new_chat_member(api, message, user_requests):
        user_id = message.new_chat_member.id
        chat_id = message.chat.id #int

        private_chat_user_ids = user_requests.get_private_chat_user_ids(chat_id)

        # chat is not private
        if private_chat_user_ids is None:
            return

        if str(user_id) in private_chat_user_ids:
            user_requests.remove_user_id_from_private_chat(str(user_id), chat_id)
            print('OK. User in chat')
        else:
            api.kik_chat_member(chat_id, user_id)
            print('haram user_id')

    @bot.catcher.catch(
        Any(
            Command(SETTINGS['bot']['password_for_update'])
        )
    )
    def update_chats(api, from_user_id, user_requests):
        if from_user_id == CONCIERGE_ID:
            usr.update_chats(api, user_requests)

    @bot.catcher.catch(
        Any(
            Command('start')
        )
    )
    def catch_ping(api, view_manager, from_user_id, chat_lang, session, user_requests):
        if from_user_id == CONCIERGE_ID:
            con.catch_ping(api, view_manager, from_user_id, chat_lang, user_requests)
        else:
            usr.catch_ping(api, view_manager, from_user_id, chat_lang, session, user_requests)

    @bot.catcher.catch(
        Any(
            MarkupButtonClicked('btn_show_first_request')
        )
    )
    def show_first_request(api, view_manager, from_user_id, chat_lang, user_requests, session):
        con.show_first_request(api, view_manager, from_user_id, chat_lang, user_requests, session)

    @bot.catcher.catch(
        Any(
            MarkupButtonClicked('btn_choose_chat')
        )
    )
    def choose_chat(api, view_manager, chat_lang, callback_query, from_user_id, session):
        if from_user_id == CONCIERGE_ID:
            con.choose_chat(api, view_manager, chat_lang, callback_query, from_user_id, session)
        else:
            usr.choose_chat(api, view_manager, chat_lang, callback_query, from_user_id, session)

    @bot.catcher.catch(
        Any(
            MarkupButtonClicked('btn_invert_chats')
        )
    )
    def invert_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        usr.invert_chats(api, view_manager, chat_lang, callback_query, from_user_id, session)

    @bot.catcher.catch(
        Any(
            MarkupButtonClicked('btn_chats_prev')
        )
    )
    def prev_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        if from_user_id == CONCIERGE_ID:
            con.prev_chats(api, view_manager, chat_lang, callback_query, from_user_id, session)
        else:
            usr.prev_chats(api, view_manager, chat_lang, callback_query, from_user_id, session)

    @bot.catcher.catch(
        Any(
            MarkupButtonClicked('btn_chats_next')
        )
    )
    def next_chats(api, view_manager, chat_lang, callback_query, from_user_id, session):
        if from_user_id == CONCIERGE_ID:
            con.next_chats(api, view_manager, chat_lang, callback_query, from_user_id, session)
        else:
            usr.next_chats(api, view_manager, chat_lang, callback_query, from_user_id, session)

    @bot.catcher.catch(
        Any(
            MarkupButtonClicked('btn_request_access')
        )
    )
    def request_access(api, view_manager, from_user_id, from_first_name,
                       from_last_name, chat_lang, callback_query, session, user_requests):
        usr.request_access(api, view_manager, from_user_id, from_first_name,
                           from_last_name, chat_lang, callback_query, session, user_requests)

    @bot.catcher.catch(
        Any(
            MarkupButtonClicked('btn_send_response')
        )
    )
    def send_response(api, view_manager, chat_lang, from_user_id, session, user_requests):
        if from_user_id == CONCIERGE_ID:
            con.send_response(api, view_manager, chat_lang, from_user_id, session, user_requests)

    @bot.catcher.catch(
        Any(
            MarkupButtonClicked('btn_reject_request')
        )
    )
    def reject_request(api, view_manager, chat_lang, from_user_id, user_requests, session):
        if from_user_id == CONCIERGE_ID:
            con.reject_request(api, view_manager, chat_lang, from_user_id, user_requests, session)

