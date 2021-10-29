from botforge.api.objects.telegram_bot import User, Message, UserProfilePhotos, File, Chat, ChatMember, \
    Update

from botforge.api.methods import APIProxy, dictify


class TelegramBotProxy(APIProxy):
    API_URL = "https://api.telegram.org/bot{token}/{method_name}"
    FILE_URL = "https://api.telegram.org/file/bot{token}/{file_url}"
    #
    ERROR_TEXTS = {'bad_response_status_code': 'Bad response status code: [{status_code}] {reason}, response = {text}',
                   'invalid_response_json': 'Server returned an invalid json: [{status_code}] {reason}, response = {text}',
                   'method_call_error': 'Method call error: [{error_code}], description = {description}'}
    #
    CONNECTION_TIMEOUT = 10
    READ_TIMEOUT = 9999

    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    @staticmethod
    def format_url(token, method_name: str):
        return TelegramBotProxy.API_URL.format(token=token, method_name=method_name)

    def format_result(self, result):
        if result.status_code != 200:
            # not everything ok
            text = TelegramBotProxy.ERROR_TEXTS['bad_response_status_code'].format(
                status_code=result.status_code, reason=result.reason, text=result.text.encode('utf-8'))
            self.report_api_error(text=text)
            return None

        json_result = None

        try:
            json_result = result.json()
        except:
            text = TelegramBotProxy.ERROR_TEXTS['invalid_response_json'].format(
                status_code=result.status_code, reason=result.reason, text=result.text.encode('utf-8'))
            self.report_api_error(text=text)
            return None

        if json_result is None or 'ok' not in json_result or not json_result['ok']:
            text = TelegramBotProxy.ERROR_TEXTS['method_call_error'].format(
                error_code=json_result['error_code'], description=json_result['description'])
            self.report_api_error(text=text)
            return None

        return json_result

    def request(self, method_name: str, method:str='get', params=None, files=None, **kwargs):
        url = self.format_url(self.bot_token, method_name)

        read_timeout = TelegramBotProxy.READ_TIMEOUT
        connection_timeout = TelegramBotProxy.CONNECTION_TIMEOUT

        if params is not None:
            if 'read_timeout' in params:
                read_timeout = params['read_timeout']

            if 'connection_timeout' in params:
                connection_timeout = params['connection_timeout']

        req_kwargs = dict(method=method, url=url, files=files,
                          timeout=(connection_timeout, read_timeout))

        if method.upper() == 'GET':
            req_kwargs['params'] = params
        elif method.upper() == 'POST':
            if files is None:
                req_kwargs['json'] = params
            else:
                req_kwargs['data'] = params

        formatted_result = self.format_result(
            self._request(**req_kwargs, **kwargs)
        )

        if formatted_result is None:
            print('Warning: no formatted result specified')
            return None

        if 'result' in formatted_result:
            return formatted_result['result']
        else:
            return None

    # helper methods

    def download_file(self, file_path):
        url = TelegramBotProxy.FILE_URL.format(token=self.bot_token, file_url=file_path)

        result = self._request(url)

        if result.status_code != 200:
            text = TelegramBotProxy.ERROR_TEXTS['bad_response_status_code'].format(
                status_code=result.status_code, reason=result.reason, text=result.text.encode('utf-8'))
            self.report_api_error(text=text)
            return None

        return result.content

    # telegram example api methods

    def get_me(self):
        result = self.request('getMe')

        return User(**result) if result is not None else None

    def create_chat_invite_link(self, chat_id, expire_date, member_limit=1):
        params = {'chat_id': chat_id,
                  'expire_date': expire_date,
                  'member_limit': member_limit
                  }

        result = self.request('createChatInviteLink', params=params)

        return result['invite_link']

    # def kick_chat_member(self, chat_id, user_id, until_date=None, revoke_messages=True):
    #     params = {'chat_id': chat_id,
    #               'user_id': user_id,
    #               'revoke_messages': revoke_messages}
    #
    #     if until_date is not None:
    #         params['until_date'] = until_date
    #
    #     result = self.request('banChatMember', params=params)
    #
    #     return result

    def send_message(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None,
                     reply_markup=None, parse_mode=None, disable_notification=None):
        params = {'text': text, 'chat_id': str(chat_id)}

        if disable_web_page_preview is not None:
            params['disable_web_page_preview'] = disable_web_page_preview

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        if parse_mode is not None:
            params['parse_mode'] = parse_mode

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        result = self.request('sendMessage', method='post', params=params)

        return Message(**result) if result is not None else None

    def forward_message(self, chat_id, from_chat_id, message_id, disable_notification=None):
        params = {'chat_id': chat_id, 'from_chat_id': from_chat_id, 'message_id': message_id}

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        result = self.request('forwardMessage', params=params)

        return Message(**result) if result is not None else None

    def send_photo(self, chat_id, photo, caption=None, disable_notification=None,
                   reply_to_message_id=None, reply_markup=None):
        params = {'chat_id': chat_id}

        if caption is not None:
            params['caption'] = caption

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        files = None

        if isinstance(photo, str):
            params['photo'] = photo
        else:
            files = {'photo': photo}

        result = self.request('sendPhoto', method='post', params=params, files=files)

        return Message(**result) if result is not None else None

    def send_audio(self, chat_id, audio, duration=None, performer=None, title=None,
                   disable_notification=None, reply_to_message_id=None, reply_markup=None):
        params = {'chat_id': chat_id}

        if duration is not None:
            params['duration'] = duration

        if performer is not None:
            params['performer'] = performer

        if title is not None:
            params['title'] = title

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        files = None

        if isinstance(audio, str):
            params['audio'] = audio
        else:
            files = {'audio': audio}

        result = self.request('sendAudio', method='post', params=params, files=files)

        return Message(**result) if result is not None else None

    def send_document(self, chat_id, document, caption=None, disable_notification=None,
                      reply_to_message_id=None, reply_markup=None):
        params = {'chat_id': chat_id}

        if caption is not None:
            params['caption'] = caption

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        files = None

        if isinstance(document, str):
            params['document'] = document
        else:
            files = {'document': document}

        result = self.request('sendDocument', params=params, files=files)

        return Message(**result) if result is not None else None

    def send_sticker(self, chat_id, sticker, disable_notification=None,
                     reply_to_message_id=None, reply_markup=None):
        params = {'chat_id': chat_id}

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        files = None

        if isinstance(sticker, str):
            params['sticker'] = sticker
        else:
            files = {'sticker': sticker}

        result = self.request('sendSticker', method='post', params=params, files=files)

        return Message(**result) if result is not None else None

    def send_video(self, chat_id, video, duration=None, width=None, height=None, caption=None,
                   disable_notification=None, reply_to_message_id=None, reply_markup=None):
        params = {'chat_id': chat_id}

        if duration is not None:
            params['duration'] = duration

        if width is not None:
            params['width'] = width

        if height is not None:
            params['height'] = height

        if caption is not None:
            params['caption'] = caption

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        files = None

        if isinstance(video, str):
            params['video'] = video
        else:
            files = {'video': video}

        result = self.request('sendVideo', method='post', params=params, files=files)

        return Message(**result) if result is not None else None

    def send_voice(self, chat_id, voice, duration, disable_notification=None,
                   reply_to_message_id=None, reply_markup=None):
        params = {'chat_id': chat_id}

        if duration is not None:
            params['duration'] = duration

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        files = None

        if isinstance(voice, str):
            params['voice'] = voice
        else:
            files = {'voice': voice}

        result = self.request('sendVoice', method='post', params=params, files=files)

        return Message(**result) if result is not None else None

    def send_location(self, chat_id, latitude, longitude, disable_notification=None,
                      reply_to_message_id=None, reply_markup=None):
        params = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude}

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        result = self.request('sendLocation', method='post', params=params)

        return Message(**result) if result is not None else None

    def send_venue(self, chat_id, latitude, longitude, title, address, foursquare_id=None,
                   disable_notification=None, reply_to_message_id=None, reply_markup=None):
        params = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude,
                  'title': title, 'address': address}

        if foursquare_id is not None:
            params['foursquare_id'] = foursquare_id

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        result = self.request('sendVenue', params=params, method='post')

        return Message(**result) if result is not None else None

    def send_contact(self, chat_id, phone_number, first_name, last_name=None,
                     disable_notification=None, reply_to_message_id=None, reply_markup=None):
        params = {'chat_id': chat_id, 'phone_number': phone_number, 'first_name': first_name}

        if last_name is not None:
            params['last_name'] = last_name

        if disable_notification is not None:
            params['disable_notification'] = disable_notification

        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        result = self.request('sendContact', params=params, method='post')

        return Message(**result) if result is not None else None

    def send_chat_action(self, chat_id, action):
        params = {'chat_id': chat_id, 'action': action}

        return self.request('sendChatAction', params=params, method='post')

    def get_user_profile_photos(self, user_id, skip=None, limit=None):
        params = {'user_id': user_id}

        if skip is not None:
            params['skip'] = skip

        if limit is not None:
            params['limit'] = limit

        result = self.request('getUserProfilePhotos', params=params, method='post')

        return UserProfilePhotos(**result) if result is not None else None

    def get_file(self, file_id):
        result = self.request('getFile', params={'file_id': file_id}, method='post')

        return File(**result) if result is not None else None

    def kik_chat_member(self, chat_id, user_id):
        params = {'chat_id': chat_id, 'user_id': user_id}

        return self.request('kickChatMember', params=params, method='post')

    def leave_chat(self, chat_id):
        params = {'chat_id': chat_id}

        return self.request('leaveChat', params=params, method='post')

    def unban_chat_member(self, chat_id, user_id):
        params = {'chat_id': chat_id, 'user_id': user_id}

        return self.request('unbanChatMember', params=params, method='post')

    def get_chat(self, chat_id):
        params = {'chat_id': chat_id}

        result = self.request('getChat', params=params, method='post')

        return Chat(**result) if result is not None else None

    def get_chat_administrators(self, chat_id):
        params = {'chat_id': chat_id}

        result = self.request('getChatAdministrators', params=params, method='post')

        return [ChatMember(**chat_member) for chat_member in result] if result is not None else None

    def get_chat_members_count(self, chat_id):
        params = {'chat_id': chat_id}

        return self.request('getChatMembersCount', params=params, method='post')

    def get_chat_member(self, chat_id, user_id):
        params = {'chat_id': chat_id, 'user_id': user_id}

        result = self.request('getChatMembersCount', params=params, method='post')

        return ChatMember(**result) if result is not None else None

    def answer_callback_query(self, callback_query_id, text=None, show_alert=None):
        params = {'callback_query_id': callback_query_id}

        if text is not None:
            params['text'] = text

        if show_alert is not None:
            params['show_alert'] = show_alert

        return self.request('answerCallbackQuery', params=params, method='post')

    def edit_message_text(self, text, chat_id=None, message_id=None, inline_message_id=None,
                          parse_mode=None, disable_web_page_preview=None, reply_markup=None):
        params = {'text': text}

        if chat_id is not None:
            params['chat_id'] = chat_id

        if message_id is not None:
            params['message_id'] = message_id

        if inline_message_id is not None:
            params['inline_message_id'] = inline_message_id

        if parse_mode is not None:
            params['parse_mode'] = parse_mode

        if disable_web_page_preview is not None:
            params['disable_web_page_preview'] = disable_web_page_preview

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        result = self.request('editMessageText', params=params, method='post')

        if result is None:
            return None

        if isinstance(result, bool):
            return result
        else:
            return Message(**result)

    def edit_message_caption(self, chat_id=None, message_id=None, inline_message_id=None, caption=None,
                             reply_markup=None):
        params = {}

        if chat_id is not None:
            params['chat_id'] = chat_id

        if message_id is not None:
            params['message_id'] = message_id

        if inline_message_id is not None:
            params['inline_message_id'] = inline_message_id

        if caption is not None:
            params['caption'] = caption

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        result = self.request('editMessageCaption', params=params, method='post')

        if result is None:
            return None

        if isinstance(result, bool):
            return result
        else:
            return Message(**result)

    def edit_message_reply_markup(self, chat_id=None, message_id=None, inline_message_id=None, reply_markup=None):
        params = {}

        if chat_id is not None:
            params['chat_id'] = chat_id

        if message_id is not None:
            params['message_id'] = message_id

        if inline_message_id is not None:
            params['inline_message_id'] = inline_message_id

        if reply_markup is not None:
            params['reply_markup'] = reply_markup.to_dict()

        result = self.request('editMessageReplyMarkup', params=params, method='post')

        if result is None:
            return None

        if isinstance(result, bool):
            return result
        else:
            return Message(**result)

    def answer_inline_query(self, inline_query_id, results, cache_time=None,
                            is_personal=None, next_offset=None, switch_pm_text=None,
                            switch_pm_parameter=None):
        params = {'inline_query_id': inline_query_id, 'results': dictify(results)}

        if cache_time is not None:
            params['cache_time'] = cache_time

        if is_personal is not None:
            params['is_personal'] = is_personal

        if next_offset is not None:
            params['next_offset'] = next_offset

        if switch_pm_text is not None:
            params['switch_pm_text'] = switch_pm_text

        if switch_pm_parameter is not None:
            params['switch_pm_parameter'] = switch_pm_parameter

        return self.request('answerInlineQuery', params=params, method='post')

    def set_webhook(self, url=None, certificate=None):
        params = {}

        if url is not None:
            params['url'] = url

        files = {}

        if certificate is not None:
            files['certificate'] = certificate

        return self.request('setWebhook', params=params, files=files, method='post')

    def get_updates(self, offset=None, limit=None, timeout=None):
        params = {}

        if offset is not None:
            params['offset'] = offset

        if limit is not None:
            params['limit'] = limit

        if timeout is not None:
            params['timeout'] = timeout

        result = self.request('getUpdates', params=params)

        return [Update(**update) for update in result] if result is not None else []
