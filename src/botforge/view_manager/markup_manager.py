import copy
import re

import itertools

from botforge.api.objects.telegram_bot import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, \
    KeyboardButton


class MarkupManager:
    DATA_ARGUMENT_SPLITTER = '|'
    TEMPLATE_ARGUMENT_SPLITTER = ','

    @staticmethod
    def parse_markup(markup_view, translator_func, markup_params: dict = None, l10n_params: dict = None, **kwargs):
        # preparations

        tree_root = markup_view['content']
        markup_id = markup_view['id']

        # helper functions

        def str_to_bool(st: str):
            return st.lower() != 'false'

        def _parse_markup_btn(btn_elem, text_format_options=None, btn_params=None, **kwargs):
            if btn_params is None:
                btn_params = dict()

            if text_format_options is None:
                text_format_options = dict()

            if btn_elem.tag != 'button':
                return None

            btn_options = copy.deepcopy(btn_elem.attrib)

            if 'id' not in btn_options:
                print('Warning: no button id specified in markup "%s"' % markup_id)
                return None

            btn_id_bare = btn_options['id']
            btn_text = translator_func(btn_id_bare, **text_format_options)

            if 'args' in btn_options:
                print(
                    'Warning: args are not supported for text markup buttons; '
                    'skipping button "%s" in markup "%s"' % (btn_id_bare, markup_id))
                return None

            if btn_text is None:
                print('Warning: no button text specified for button with id "%s" in markup "%s"' %
                      (btn_id_bare, markup_id))
                btn_text = btn_id_bare

            if 'text' in btn_options:
                del btn_options['text']

            if 'show-if' in btn_options:
                condition_var_name = btn_options['show-if']

                if condition_var_name[0] != ':':
                    print('Warning: button "%s" in markup "%s" has a wrong condition var; skipped' % (
                        btn_id_bare, markup_id))
                    return None

                # skip the dots
                condition_var_name = condition_var_name[1:]

                # check if it is an inverted condition we have here
                condition_is_inverted = condition_var_name[0] == '!'

                if condition_is_inverted:
                    # if it is - let us find out the real variable name
                    condition_var_name = condition_var_name[1:]

                condition_var_val = btn_params.get(condition_var_name)

                if condition_var_val in [None, False]:
                    # btn does not satisfy the condition
                    if not condition_is_inverted:
                        return None
                else:
                    # btn satisfies the condition
                    # .. unless the condition is inverted!
                    if condition_is_inverted:
                        return None

                del btn_options['show-if']

            del btn_options['id']

            if 'mask' in btn_options:
                del btn_options['mask']

            return KeyboardButton(text=btn_text, **btn_options)

        def _parse_inline_markup_btn(btn_elem, text_format_options=None, index_id_postfix=None, btn_params=None,
                                     **kwargs):
            if btn_params is None:
                btn_params = dict()

            if text_format_options is None:
                text_format_options = dict()

            if btn_elem.tag != 'button':
                return None

            btn_options = copy.deepcopy(btn_elem.attrib)

            if 'id' not in btn_options:
                print('Warning: no button id specified in markup "%s"' % markup_id)
                return None

            btn_id_bare = btn_options['id']
            btn_text = translator_func(btn_id_bare, **text_format_options)

            if btn_text is None:
                print('Warning: no button text specified for button with id "%s" in markup "%s"' %
                      (btn_id_bare, markup_id))
                btn_text = btn_id_bare

            if 'id-postfix-type' in btn_options:
                postfix_type = btn_options.get('id-postfix-type')

                if postfix_type == 'index' and index_id_postfix is not None:
                    btn_id_bare += '_%s' % str(index_id_postfix + 1)
                    btn_options['id'] = btn_id_bare
                else:
                    print('Warning: cannot create postfix "%s" for button %s, skipped ' % (postfix_type, btn_id_bare))

                del btn_options['id-postfix-type']

            if 'args' in btn_options:
                btn_id_args = btn_options['args'].split(MarkupManager.TEMPLATE_ARGUMENT_SPLITTER)
                id_complements = []

                for arg in btn_id_args:
                    if arg[0] == ':':
                        # for support of global variables
                        val = btn_params.get(arg[1:])

                        if val is not None:
                            id_complements.append(val)
                    else:
                        # for support of local variables that are cycle items
                        val = btn_params.get(arg)

                        if val is not None:
                            id_complements.append(val)

                # TODO: make sure id length does not exceed 64 characters

                btn_options['id'] = MarkupManager.DATA_ARGUMENT_SPLITTER.join([btn_id_bare, *id_complements])

                del btn_options['args']

            if 'show-if' in btn_options:
                condition_var_name = btn_options['show-if']

                if condition_var_name[0] != ':':
                    print('Warning: button "%s" in markup "%s" has a wrong condition var; skipped' % (
                        btn_id_bare, markup_id))
                    return None

                # skip the dots
                condition_var_name = condition_var_name[1:]

                # check if it is an inverted condition we have here
                condition_is_inverted = condition_var_name[0] == '!'

                if condition_is_inverted:
                    # if it is - let us find out the real variable name
                    condition_var_name = condition_var_name[1:]

                condition_var_val = btn_params.get(condition_var_name)

                if condition_var_val in [None, False]:
                    # btn does not satisfy the condition
                    if not condition_is_inverted:
                        return None
                else:
                    # btn satisfies the condition
                    # .. unless the condition is inverted!
                    if condition_is_inverted:
                        return None

                del btn_options['show-if']

            if 'mask' in btn_options:
                del btn_options['mask']

            if 'url' in btn_options:
                url_var_name = btn_options['url']

                if url_var_name[0] != ':':
                    print('Warning: url parameter at button "%s" in markup "%s" must start from ":"; skipped' % (
                        btn_id_bare, markup_id))
                    return None

                url_var_name = url_var_name[1:]

                url_var_val = btn_params.get(url_var_name)

                if url_var_name in [None, False]:
                    print('Error: button "%s" in markup "%s" has a missed url value; skipped' % (btn_id_bare, markup_id))
                    return None

                else:
                    btn_options['url'] = url_var_val

            return InlineKeyboardButton(text=btn_text, callback_data=btn_options['id'], **btn_options)

        def _parse_btns_no_collection(collection_elem, parser_func, text_format_options):
            btns = []

            for btn_elem in collection_elem:
                if btn_elem.tag == 'button':
                    btn = parser_func(btn_elem=btn_elem,
                                      text_format_options=text_format_options,
                                      btn_params=markup_params)

                    if btn is not None:
                        btns.append(btn)

            return btns

        def _parse_btns_from_collection(collection, tree_elem, parser_func, text_format_options):
            btns = []

            btn_elements = [btn_elem for btn_elem in tree_elem if btn_elem.tag == 'button']
            btn_elements_generator = itertools.cycle(btn_elements)

            for item_index, collection_item in enumerate(collection):
                next_btn_elem = next(btn_elements_generator)
                btn = parser_func(btn_elem=next_btn_elem,
                                  text_format_options={**text_format_options, **collection_item},
                                  index_id_postfix=item_index,
                                  btn_params={**markup_params, **collection_item})
                btns.append(btn)

            return btns

        # preparations

        kb = None  # no markup by default
        parser_func = None

        if tree_root.tag == 'markup':
            resize_keyboard = str_to_bool(tree_root.attrib.get('resize_keyboard', 'false'))
            one_time_keyboard = str_to_bool(tree_root.attrib.get('one_time_keyboard', 'false'))
            selective = str_to_bool(tree_root.attrib.get('selective', 'false'))

            kb = ReplyKeyboardMarkup(resize_keyboard=resize_keyboard,
                                     one_time_keyboard=one_time_keyboard,
                                     selective=selective)
            parser_func = _parse_markup_btn
        elif tree_root.tag == 'inline-markup':
            kb = InlineKeyboardMarkup()
            parser_func = _parse_inline_markup_btn

        # traverse the tree

        for tree_elem in tree_root:
            if tree_elem.tag not in ['row', 'column']:
                print('Warning: unsupported tag within the root element: "%s"' % tree_elem.tag)
                continue

            # apply show-if attribute
            if 'show-if' in tree_elem.attrib:
                condition_var_name = tree_elem.attrib['show-if']

                if condition_var_name[0] != ':':
                    print('Warning: row in markup "%s" has a wrong condition var; skipped' % markup_id)
                    continue

                # skip the dots
                condition_var_name = condition_var_name[1:]

                # check if it is an inverted condition we have here
                condition_is_inverted = condition_var_name[0] == '!'

                if condition_is_inverted:
                    # if it is - let us find out the real variable name
                    condition_var_name = condition_var_name[1:]

                condition_var_val = markup_params.get(condition_var_name)

                if condition_var_val in [None, False]:
                    # btn does not satisfy the condition
                    if not condition_is_inverted:
                        continue
                else:
                    # btn satisfies the condition
                    # .. unless the condition is inverted!
                    if condition_is_inverted:
                        continue

            # check if the row/column is to be expanded from a collection
            collection = None

            if 'collection' not in tree_elem.attrib:
                # collection is still None
                pass
            else:
                # retrieve the collection
                collection_name = tree_elem.attrib.get('collection')

                if collection_name not in markup_params:
                    # no collection provided - skip that tag
                    print(
                        'Warning: "collection" attribute is not present in view_params of "%s" markup, skipped' % markup_id)
                    continue

                collection = markup_params.get(collection_name)

            if tree_elem.tag == 'row':
                row_buttons = []

                if collection is None:
                    # just plain buttons

                    row_buttons.extend(_parse_btns_no_collection(tree_elem, parser_func, l10n_params))
                else:
                    # collection of buttons

                    row_buttons.extend(_parse_btns_from_collection(collection, tree_elem, parser_func, l10n_params))

                if len(row_buttons) > 0:
                    kb.row(*row_buttons)
            elif tree_elem.tag == 'column':
                column_buttons = []

                if collection is None:
                    # just plain buttons
                    column_buttons.extend(_parse_btns_no_collection(tree_elem, parser_func, l10n_params))
                else:
                    # collection of buttons
                    column_buttons.extend(_parse_btns_from_collection(collection, tree_elem, parser_func, l10n_params))

                if len(column_buttons) > 0:
                    for btn in column_buttons:
                        kb.row(*[btn])

        return kb

    @staticmethod
    def resolve_button_arguments(_views, data, markup_id: str, btn_id: str):
        """ Not used yet. """
        if data is None:
            return dict()

        if markup_id not in _views.get('markups', {}):
            return dict()

        tags_to_check = [_views.get('markups', {}).get(markup_id, {}).get('content')]
        wanted_tag = None

        while len(tags_to_check) > 0:
            current_tag = tags_to_check.pop(0)

            if current_tag is None:
                # TODO: do know why now, but it can hurt
                continue

            if current_tag.tag == 'button' and 'id' in current_tag.attrib:
                if current_tag.attrib.get('id') == btn_id:
                    wanted_tag = current_tag
                    break

            child_tags = [tag for tag in current_tag]
            tags_to_check.extend(child_tags)

        if wanted_tag is None:
            return dict()

        btn_args = wanted_tag.attrib.get('args').split(MarkupManager.TEMPLATE_ARGUMENT_SPLITTER)

        for index, btn_arg in enumerate(btn_args):
            if len(btn_arg) > 1 and btn_arg[0] == ':':
                btn_args[index] = btn_arg[1:]

        if btn_args is None:
            return []

        resolved_btn_args = dict(zip(btn_args, data.split(MarkupManager.DATA_ARGUMENT_SPLITTER)[1:]))

        return resolved_btn_args

    @staticmethod
    def text_matches_btn(markup_views, message_text: str, btn_id: str):
        if message_text is None:
            return False

        tags_to_check = [v['content'] for v in markup_views.values()]
        wanted_tag = None

        while len(tags_to_check) > 0:
            current_tag = tags_to_check.pop(0)

            if current_tag.tag == 'button' and 'id' in current_tag.attrib:
                if current_tag.attrib.get('id') == btn_id:
                    wanted_tag = current_tag
                    break

            child_tags = [tag for tag in current_tag]
            tags_to_check.extend(child_tags)

        if wanted_tag is None:
            print('Warning: no button with id "%s" found' % btn_id)
            return False

        if 'mask' not in wanted_tag.attrib:
            # print('Warning: button with id "%s" has no mask attribute so can not be recognized' % btn_id)
            return False

        button_mask = wanted_tag.attrib.get('mask')

        # whether given message text matches the button id given
        return re.match(button_mask, message_text) is not None
