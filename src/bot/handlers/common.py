import copy

from botforge.api.consts.telegram_bot import ParseMode
from botforge.catcher.match import Any
from botforge.matches import Command, MarkupButtonClicked

ALL_CHATS = [{'chat_id': 123, 'title': 'Test chat', 'is_chosen': True}]


def mount(bot):
    def render_available_chats(chosen_chats_ids):
        available_chats_rendered = []

        for chat in ALL_CHATS:
            chat_params = copy.deepcopy(chat)
            chat_params['is_chosen'] = '🔘' if chat['chat_id'] in chosen_chats_ids else '⚪️'
            chat_params = {k: str(v) for k, v in chat_params.items()}
            available_chats_rendered.append(chat_params)

        return available_chats_rendered

    @bot.catcher.catch(
        Any(
            Command('start'),
        )
    )
    def catch_ping(api, view_manager, from_user_id, chat_lang, session):
        chosen_chats_ids = session['chosen_chats_ids'] if 'chosen_chats_ids' in session else []
        params = {'available_chats': render_available_chats(chosen_chats_ids)}
        message_text = view_manager.get_view('request_chats_access_screen', chat_lang, screen_params={'total_chats': len(ALL_CHATS)})
        kb = view_manager.get_view('request_chats_access_markup', chat_lang,
                                   markup_params=params)

        api.send_message(from_user_id, message_text, reply_markup=kb, parse_mode=ParseMode.html)

    @bot.catcher.catch(
        Any(
            MarkupButtonClicked('btn_choose_chat'),
        )
    )
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

        params = {'available_chats': render_available_chats(chosen_chats_ids)}
        message_text = view_manager.get_view('request_chats_access_screen', chat_lang,
                                             screen_params={'total_chats': len(ALL_CHATS)})
        kb = view_manager.get_view('request_chats_access_markup', chat_lang,
                                   markup_params=params)

        api.edit_message_text(message_text,
                              chat_id=from_user_id,
                              message_id=current_message_id,
                              reply_markup=kb,
                              parse_mode=ParseMode.html)

