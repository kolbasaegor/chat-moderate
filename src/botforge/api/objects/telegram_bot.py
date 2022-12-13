# -*- coding: utf-8 -*-
from botforge.catcher.exceptions import UnexpectedObjectType
from botforge.api.objects import JsonSerializable


class Update(JsonSerializable):
    def __init__(self, update_id, message=None, edited_message=None, inline_query=None,
                 chosen_inline_result=None, callback_query=None, **kwargs):
        self.message = Message(**message) if message is not None else None
        self.edited_message = Message(**edited_message) if edited_message is not None else None
        self.inline_query = InlineQuery(**inline_query) if inline_query is not None else None
        self.chosen_inline_result = ChosenInlineResult(
            **chosen_inline_result) if chosen_inline_result is not None else None

        if callback_query is not None:
            callback_query['from_user'] = callback_query['from']
            del callback_query['from']

            self.callback_query = CallbackQuery(**callback_query)
        else:
            self.callback_query = None

        super().__init__(update_id=update_id, **kwargs)


class User(JsonSerializable):
    def __init__(self, id, first_name, last_name=None, username=None, **kwargs):
        super().__init__(id=id, first_name=first_name, last_name=last_name,
                         username=username, **kwargs)


class Chat(JsonSerializable):
    def __init__(self, id, type, title=None, username=None, first_name=None, last_name=None, **kwargs):
        super().__init__(id=id, type=type, title=title, username=username,
                         first_name=first_name, last_name=last_name, **kwargs)


class Message(JsonSerializable):
    def __init__(self, message_id, date, chat, from_user=None, forward_from=None,
                 forward_from_chat=None, forward_date=None, reply_to_message=None,
                 edit_date=None, text=None, entities=None, audio=None,
                 document=None, photo=None, sticker=None, video=None,
                 voice=None, caption=None, contact=None, location=None,
                 venue=None, new_chat_member=None, left_chat_member=None,
                 new_chat_title=None, new_chat_photo=None, delete_chat_photo=None,
                 pinned_message=None, group_chat_created=None,
                 supergroup_chat_created=None, channel_chat_created=None,
                 migrate_to_chat_id=None, migrate_from_chat_id=None, **kwargs):
        content_type = None

        if from_user is not None:
            self.from_user = User(**from_user)
        elif 'from' in kwargs:
            self.from_user = User(**kwargs['from'])
            del kwargs['from']

        self.chat = Chat(**chat)

        self.forward_from = User(**forward_from) if forward_from is not None else None
        self.forward_from_chat = Chat(**forward_from_chat) if forward_from_chat is not None else None
        self.reply_to_message = Message(**reply_to_message) if reply_to_message is not None else None
        self.entities = [MessageEntity(**entity) for entity in entities] if entities is not None else []

        if audio is not None:
            self.audio = Audio(**audio)
            content_type = 'audio'
        else:
            self.audio = None

        if document is not None:
            self.document = Document(**document)
            content_type = 'document'
        else:
            self.document = None

        if photo is not None:
            self.photo = [PhotoSize(**photo_size) for photo_size in photo]
            content_type = 'photo'
        else:
            self.photo = None

        if sticker is not None:
            self.sticker = Sticker(**sticker)
            content_type = 'sticker'
        else:
            self.sticker = None

        if video is not None:
            self.video = Video(**video)
            content_type = 'video'
        else:
            self.video = None

        if voice is not None:
            self.voice = Voice(**voice)
            content_type = 'voice'
        else:
            self.voice = None

        if contact is not None:
            self.contact = Contact(**contact)
            content_type = 'contact'
        else:
            self.contact = None

        if location is not None:
            self.location = Location(**location)
            content_type = 'location'
        else:
            self.location = None

        if venue is not None:
            self.venue = Venue(**venue)
            content_type = 'venue'
        else:
            self.venue = None

        if new_chat_member is not None:
            self.new_chat_member = User(**new_chat_member)
            content_type = 'new_chat_member'
        else:
            self.new_chat_member = None

        if left_chat_member is not None:
            self.left_chat_member = User(**left_chat_member)
            content_type = 'left_chat_member'
        else:
            self.left_chat_member = None

        if new_chat_photo is not None:
            self.new_chat_photo = [PhotoSize(**photo_size) for photo_size in new_chat_photo]
            content_type = 'new_chat_photo'
        else:
            self.new_chat_photo = None

        self.pinned_message = Message(**pinned_message) if pinned_message is not None else None

        if content_type is None:
            if text is not None:
                content_type = 'text'

        super().__init__(message_id=message_id, date=date, forward_date=forward_date,
                         edit_date=edit_date, text=text, caption=caption,
                         new_chat_title=new_chat_title, delete_chat_photo=delete_chat_photo,
                         group_chat_created=group_chat_created,
                         supergroup_chat_created=supergroup_chat_created,
                         channel_chat_created=channel_chat_created,
                         migrate_to_chat_id=migrate_to_chat_id,
                         migrate_from_chat_id=migrate_from_chat_id,
                         content_type=content_type,
                         **kwargs)


class MessageEntity(JsonSerializable):
    def __init__(self, type, offset, length, url=None, user=None, **kwargs):
        self.user = User(**user) if user is not None else None

        super().__init__(type=type, offset=offset, length=length, url=url, **kwargs)


class PhotoSize(JsonSerializable):
    def __init__(self, file_id, width, height, file_size=None, **kwargs):
        super().__init__(file_id=file_id, width=width, height=height,
                         file_size=file_size, **kwargs)


class Audio(JsonSerializable):
    def __init__(self, file_id, duration, performer=None, title=None, mime_type=None,
                 file_size=None, **kwargs):
        super().__init__(file_id=file_id, duration=duration, performer=performer,
                         title=title, mime_type=mime_type, file_size=file_size, **kwargs)


class Document(JsonSerializable):
    def __init__(self, file_id, thumb=None, file_name=None, mime_type=None,
                 file_size=None, **kwargs):
        self.thumb = PhotoSize(**thumb) if thumb is not None else None

        super().__init__(file_id=file_id, file_name=file_name,
                         mime_type=mime_type, file_size=file_size, **kwargs)


class Sticker(JsonSerializable):
    def __init__(self, file_id, width, height, thumb=None, emoji=None, file_size=None, **kwargs):
        self.thumb = PhotoSize(**thumb) if thumb is not None else None

        super().__init__(file_id=file_id, width=width, height=height,
                         emoji=emoji, file_size=file_size, **kwargs)


class Video(JsonSerializable):
    def __init__(self, file_id, width, height, duration, thumb=None, mime_type=None,
                 file_size=None, **kwargs):
        self.thumb = PhotoSize(**thumb) if thumb is not None else None

        super().__init__(file_id=file_id, width=width, height=height,
                         duration=duration, mime_type=mime_type, file_size=file_size,
                         **kwargs)


class Voice(JsonSerializable):
    def __init__(self, file_id, duration, mime_type=None, file_size=None, **kwargs):
        super().__init__(file_id=file_id, duration=duration, mime_type=mime_type,
                         file_size=file_size, **kwargs)


class Contact(JsonSerializable):
    def __init__(self, phone_number, first_name, last_name=None, user_id=None, **kwargs):
        super().__init__(phone_number=phone_number, first_name=first_name,
                         last_name=last_name, user_id=user_id, **kwargs)


class Location(JsonSerializable):
    def __init__(self, longitude, latitude, **kwargs):
        super().__init__(longitude=longitude, latitude=latitude, **kwargs)


class Venue(JsonSerializable):
    def __init__(self, location, title, address, foursquare_id=None, **kwargs):
        self.location = Location(**location)

        super().__init__(title=title, address=address,
                         foursquare_id=foursquare_id, **kwargs)


class UserProfilePhotos(JsonSerializable):
    def __init__(self, total_count, photos, **kwargs):
        self.photos = [[PhotoSize(**y) for y in x] for x in photos]
        super().__init__(total_count=total_count, **kwargs)


class File(JsonSerializable):
    def __init__(self, file_id, file_size=None, file_path=None, **kwargs):
        super().__init__(file_id=file_id, file_size=file_size,
                         file_path=file_path, **kwargs)


class ReplyKeyboardMarkup(JsonSerializable):
    def __init__(self, keyboard=None, resize_keyboard=False,
                 one_time_keyboard=False, selective=None, row_width=3,
                 **kwargs):
        if keyboard is None:
            keyboard = []

        super().__init__(keyboard=keyboard, resize_keyboard=resize_keyboard,
                         one_time_keyboard=one_time_keyboard,
                         selective=selective, row_width=row_width,
                         **kwargs)

    def add(self, *buttons):
        key_num = 1
        row = []

        for button in buttons:
            if isinstance(button, str):
                row.append(KeyboardButton(text=button))
            elif isinstance(button, JsonSerializable):
                row.append(KeyboardButton(button))
            elif isinstance(button, dict):
                row.append(KeyboardButton(**button))
            else:
                raise UnexpectedObjectType()

            if key_num % self.row_width == 0:
                self.keyboard.append(row)
                row = []

            key_num += 1

        if len(row) > 0:
            self.keyboard.append(row)

    def row(self, *buttons):
        btn_array = []

        for button in buttons:
            if isinstance(button, str):
                btn_array.append({'text': button})
            elif isinstance(button, JsonSerializable):
                btn_array.append(button)
            else:
                raise UnexpectedObjectType()

        self.keyboard.append(btn_array)

        return self


class KeyboardButton(JsonSerializable):
    def __init__(self, text, request_contact=False, request_location=False, **kwargs):
        if request_contact:
            self.request_contact = True
        elif request_location:
            self.request_location = True

        super().__init__(text=text, **kwargs)


class ReplyKeyboardHide(JsonSerializable):
    def __init__(self, selective=None, **kwargs):
        super().__init__(selective=selective, hide_keyboard=True, **kwargs)


class InlineKeyboardMarkup(JsonSerializable):
    def __init__(self, inline_keyboard=None, row_width=3, **kwargs):
        if inline_keyboard is None:
            inline_keyboard = []

        super().__init__(inline_keyboard=inline_keyboard, row_width=row_width, **kwargs)

    def add(self, *buttons):
        key_num = 1
        row = []

        for button in buttons:
            if isinstance(button, JsonSerializable):
                row.append(InlineKeyboardButton(**button.to_dict()))
            else:
                raise UnexpectedObjectType()

            if key_num % self.row_width == 0:
                self.inline_keyboard.append(row)
                row = []

            key_num += 1

        if len(row) > 0:
            self.inline_keyboard.append(row)

    def row(self, *buttons):
        if len(buttons) < 1:
            return self

        btn_array = []

        for button in buttons:
            if isinstance(button, JsonSerializable):
                btn_array.append(InlineKeyboardButton(**button.to_dict()))
            else:
                raise UnexpectedObjectType()

        self.inline_keyboard.append(btn_array)

        return self


class InlineKeyboardButton(JsonSerializable):
    def __init__(self, text, url=None, callback_data=None, switch_inline_query=None, **kwargs):
        super().__init__(text=text, url=url, callback_data=callback_data,
                         switch_inline_query=switch_inline_query, **kwargs)


class CallbackQuery(JsonSerializable):
    def __init__(self, id, from_user, data, message=None, inline_message_id=None, **kwargs):
        self.from_user = User(**from_user) if from_user is not None else None
        self.message = Message(**message) if message is not None else None

        super().__init__(id=id, data=data, inline_message_id=inline_message_id, **kwargs)


class ForceReply(JsonSerializable):
    def __init__(self, selective=None, **kwargs):
        super().__init__(force_reply=True, selective=selective, **kwargs)


class ChatMember(JsonSerializable):
    def __init__(self, user, status, **kwargs):
        self.user = User(**user)

        super().__init__(status=status, **kwargs)


class InlineQuery(JsonSerializable):
    def __init__(self, id, from_user, query, offset, location=None, **kwargs):
        self.from_user = User(**from_user)
        self.location = Location(**location) if location is not None else None

        super().__init__(id=id, query=query, offset=offset, **kwargs)


# Inline query results


class InlineQueryResult(JsonSerializable):
    def __init__(self, type, id, **kwargs):
        super().__init__(type=type, id=id, **kwargs)


def get_message_input_content(input_message_content):
    if 'message_text' in input_message_content:
        return InputTextMessageContent(**input_message_content)
    elif 'address' in input_message_content:
        return InputVenueMessageContent(**input_message_content)
    elif 'phone_number' in input_message_content:
        return InputContactMessageContent(**input_message_content)
    elif 'latitude' in input_message_content:
        return InputLocationMessageContent(**input_message_content)
    else:
        return None


class InlineQueryResultArticle(InlineQueryResult):
    def __init__(self, id, title, input_message_content, reply_markup=None, url=None,
                 hide_url=None, description=None, thumb_url=None, thumb_width=None,
                 thumb_height=None, **kwargs):
        self.input_message_content = get_message_input_content(input_message_content)
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None

        super().__init__(type='article', id=id, title=title, url=url,
                         hide_url=hide_url, description=description,
                         thumb_url=thumb_url, thumb_width=thumb_width,
                         thumb_height=thumb_height, **kwargs)


class InlineQueryResultPhoto(InlineQueryResult):
    def __init__(self, id, photo_url, thumb_url, photo_width=None, photo_height=None, title=None,
                 description=None, caption=None, reply_markup=None, input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(id=id, type='photo', photo_url=photo_url,
                         thumb_url=thumb_url, photo_width=photo_width,
                         photo_height=photo_height, title=title,
                         description=description, caption=caption, **kwargs)


class InlineQueryResultGif(InlineQueryResult):
    def __init__(self, id, gif_url, thumb_url, gif_width=None, gif_height=None, title=None,
                 caption=None, reply_markup=None, input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(id=id, type='gif', gif_url=gif_url,
                         thumb_url=thumb_url, gif_width=gif_width,
                         gif_height=gif_height, title=title,
                         caption=caption, **kwargs)


class InlineQueryResultMpeg4Gif(InlineQueryResult):
    def __init__(self, id, mpeg4_url, thumb_url, mpeg4_width=None, mpeg4_height=None, title=None,
                 caption=None, reply_markup=None, input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(id=id, type='mpeg4_gif', mpeg4_url=mpeg4_url,
                         thumb_url=thumb_url, mpeg4_width=mpeg4_width,
                         mpeg4_height=mpeg4_height, title=title,
                         caption=caption, **kwargs)


class InlineQueryResultVideo(InlineQueryResult):
    def __init__(self, id, title, video_url, thumb_url, mime_type, video_width=None,
                 video_height=None, video_duration=None, caption=None, description=None,
                 reply_markup=None, input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(id=id, type='video', video_url=video_url,
                         thumb_url=thumb_url, mime_type=mime_type,
                         video_width=video_width, video_height=video_height,
                         video_duration=video_duration, title=title,
                         caption=caption, description=description, **kwargs)


class InlineQueryResultAudio(InlineQueryResult):
    def __init__(self, id, audio_url, title, performer=None, audio_duration=None, reply_markup=None,
                 input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(id=id, type='audio', title=title, audio_url=audio_url,
                         performer=performer, audio_duration=audio_duration, **kwargs)


class InlineQueryResultVoice(InlineQueryResult):
    def __init__(self, id, voice_url, title, voice_duration=None, reply_markup=None,
                 input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='voice', id=id, voice_url=voice_url, voice_duration=voice_duration,
                         title=title, **kwargs)


class InlineQueryResultDocument(InlineQueryResult):
    def __init__(self, id, title, document_url, mime_type, caption=None, description=None, reply_markup=None,
                 input_message_content=None, thumb_url=None, thumb_width=None, thumb_height=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='document', id=id, title=title, caption=caption,
                         document_url=document_url, mime_type=mime_type,
                         description=description, thumb_url=thumb_url,
                         thumb_width=thumb_width, thumb_height=thumb_height, **kwargs)


class InlineQueryResultLocation(InlineQueryResult):
    def __init__(self, id, title, latitude, longitude, reply_markup=None, input_message_content=None,
                 thumb_url=None, thumb_width=None, thumb_height=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='location', id=id, latitude=latitude, longitude=longitude, title=title,
                         thumb_url=thumb_url, thumb_height=thumb_height, thumb_width=thumb_width, **kwargs)


class InlineQueryResultVenue(InlineQueryResult):
    def __init__(self, id, title, latitude, longitude, address, foursquare_id=None, reply_markup=None,
                 input_message_content=None, thumb_url=None, thumb_width=None, thumb_height=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='venue', id=id, title=title, latitude=latitude, longitude=longitude, address=address,
                         foursquare_id=foursquare_id, thumb_url=thumb_url, thumb_width=thumb_width,
                         thumb_height=thumb_height, **kwargs)


class InlineQueryResultContact(InlineQueryResult):
    def __init__(self, id, phone_number, first_name, last_name=None, reply_markup=None,
                 input_message_content=None, thumb_url=None, thumb_width=None, thumb_height=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='contact', id=id, phone_number=phone_number, first_name=first_name, last_name=last_name,
                         thumb_url=thumb_url, thumb_width=thumb_width, thumb_height=thumb_height, **kwargs)


class InlineQueryResultCached(InlineQueryResult):
    def __init__(self, id, type, **kwargs):
        super().__init__(id, type, **kwargs)


class InlineQueryResultCachedPhoto(InlineQueryResultCached):
    def __init__(self, id, photo_file_id, title=None, description=None, caption=None, reply_markup=None,
                 input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='photo', id=id, photo_file_id=photo_file_id, title=title,
                         description=description, caption=caption, **kwargs)


class InlineQueryResultCachedGif(InlineQueryResultCached):
    def __init__(self, id, gif_file_id, title=None, caption=None, reply_markup=None,
                 input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='gif', id=id, gif_file_id=gif_file_id, title=title,
                         caption=caption, **kwargs)


class InlineQueryResultCachedMpeg4Gif(InlineQueryResultCached):
    def __init__(self, id, mpeg4_file_id, title=None, caption=None, reply_markup=None,
                 input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='mpeg4_gif', id=id, mpeg4_file_id=mpeg4_file_id, title=title,
                         caption=caption, **kwargs)


class InlineQueryResultCachedSticker(InlineQueryResultCached):
    def __init__(self, id, sticker_file_id, reply_markup=None, input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='sticker', id=id, sticker_file_id=sticker_file_id, **kwargs)


class InlineQueryResultCachedDocument(InlineQueryResultCached):
    def __init__(self, id, document_file_id, title, description=None, caption=None, reply_markup=None,
                 input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='document', id=id, title=title, document_file_id=document_file_id,
                         description=description, caption=caption, **kwargs)


class InlineQueryResultCachedVideo(InlineQueryResultCached):
    def __init__(self, id, video_file_id, title, description=None, caption=None, reply_markup=None,
                 input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='video', id=id, video_file_id=video_file_id, title=title,
                         description=description, caption=caption, **kwargs)


class InlineQueryResultCachedVoice(InlineQueryResultCached):
    def __init__(self, id, voice_file_id, title, type, reply_markup=None, input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='voice', id=id, title=title, voice_file_id=voice_file_id, **kwargs)


class InlineQueryResultCachedAudio(InlineQueryResultCached):
    def __init__(self, id, audio_file_id, reply_markup=None, input_message_content=None, **kwargs):
        self.reply_markup = InlineKeyboardMarkup(**reply_markup) if reply_markup is not None else None
        self.input_message_content = get_message_input_content(input_message_content) \
            if input_message_content is not None else None

        super().__init__(type='audio', id=id, audio_file_id=audio_file_id, **kwargs)


# InputMessageContent


class InputMessageContent(JsonSerializable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class InputTextMessageContent(InputMessageContent):
    def __init__(self, message_text, parse_mode=None, disable_web_page_preview=False, **kwargs):
        super().__init__(message_text=message_text, parse_mode=parse_mode,
                         disable_web_page_preview=disable_web_page_preview, **kwargs)


class InputLocationMessageContent(InputMessageContent):
    def __init__(self, latitude, longitude, **kwargs):
        super().__init__(latitude=latitude, longitude=longitude, **kwargs)


class InputVenueMessageContent(InputMessageContent):
    def __init__(self, latitude, longitude, title, address, foursquare_id=None, **kwargs):
        super().__init__(latitude=latitude, longitude=longitude, title=title, address=address,
                         foursquare_id=foursquare_id, **kwargs)


class InputContactMessageContent(InputMessageContent):
    def __init__(self, phone_number, first_name, last_name=None, **kwargs):
        super().__init__(phone_number=phone_number, first_name=first_name,
                         last_name=last_name, **kwargs)


#


class ChosenInlineResult(JsonSerializable):
    def __init__(self, result_id, from_user, query, location=None, inline_message_id=None, **kwargs):
        self.from_user = User(**from_user)
        self.location = Location(**location) if location is not None else None

        super().__init__(result_id=result_id, query=query, inline_message_id=inline_message_id,
                         **kwargs)
