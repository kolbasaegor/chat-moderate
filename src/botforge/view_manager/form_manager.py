from botforge.view_manager.markup_manager import MarkupManager
from botforge.view_manager.screen_manager import ScreenManager


class FormManager:
    @staticmethod
    def parse_form(form_view, all_views, translator_func, form_params: dict = None, l10n_params: dict = None, **kwargs):
        # preparations

        tree_root = form_view['content']
        form_id = form_view['id']

        if form_id is None:
            print('Warning: could not parse a form: no form id specified')
            return None

        message = {}

        for tree_elem in tree_root:
            if tree_elem.tag not in ['screen', 'markup', 'inline-markup']:
                print('Warning: unsupported tag within the message element: "%s"' % tree_elem.tag)
                continue

            if tree_elem.tag == 'screen':
                this_screen_is_visible = True

                if 'show-if' in tree_elem.attrib:
                    condition_var_name = tree_elem.attrib.get('show-if')

                    if condition_var_name[0] != ':':
                        print('Warning: one screen of form "%s" has a wrong condition var; skipped' % form_id)
                        return None

                    # skip the dots
                    condition_var_name = condition_var_name[1:]

                    # check if it is an inverted condition we have here
                    condition_is_inverted = condition_var_name[0] == '!'

                    if condition_is_inverted:
                        # if it is - let us find out the real variable name
                        condition_var_name = condition_var_name[1:]

                    condition_var_val = form_params.get(condition_var_name)

                    if condition_var_val in [None, False]:
                        # screen does not satisfy the condition
                        if not condition_is_inverted:
                            this_screen_is_visible = False
                    else:
                        # screen satisfies the condition
                        # .. unless the condition is inverted!
                        if condition_is_inverted:
                            this_screen_is_visible = False

                if 'screen' in message or not this_screen_is_visible:
                    print('Warning: screen for form "%s" has already been chosen; skipped' % form_id, flush=True)
                    continue

                screen_id = tree_elem.attrib.get('id')
                screen_view = None

                if screen_id is not None:
                    # get a prepared screen
                    screen_view = all_views['screens'].get(screen_id)
                else:
                    # get an inline screen
                    screen_view = {
                        'id': '{form_id}_screen'.format(form_id=form_id),
                        'content': tree_elem,
                        'filename': form_view['filename']
                    }

                if screen_view is None:
                    print('Warning: screen view with id = "%s" not found; skipped' % screen_id)
                    continue

                message['screen'] = ScreenManager.parse_screen(screen_view, translator_func,
                                                               form_params, l10n_params)

            elif tree_elem.tag in ['markup', 'inline-markup']:
                this_markup_is_visible = True

                if 'show-if' in tree_elem.attrib:
                    condition_var_name = tree_elem.attrib.get('show-if')

                    if condition_var_name[0] != ':':
                        print('Warning: one markup of form "%s" has a wrong condition var; skipped' % form_id)
                        return None

                    # skip the dots
                    condition_var_name = condition_var_name[1:]

                    # check if it is an inverted condition we have here
                    condition_is_inverted = condition_var_name[0] == '!'

                    if condition_is_inverted:
                        # if it is - let us find out the real variable name
                        condition_var_name = condition_var_name[1:]

                    condition_var_val = form_params.get(condition_var_name)

                    if condition_var_val in [None, False]:
                        # screen does not satisfy the condition
                        if not condition_is_inverted:
                            this_markup_is_visible = False
                    else:
                        # screen satisfies the condition
                        # .. unless the condition is inverted!
                        if condition_is_inverted:
                            this_markup_is_visible = False

                if 'markup' in message or not this_markup_is_visible:
                    print('Warning: markup for form "%s" has already been chosen; skipped' % form_id, flush=True)
                    continue

                markup_id = tree_elem.attrib.get('id')
                markup_view = None

                if markup_id is not None:
                    markup_view = all_views['markups'].get(markup_id)
                else:
                    markup_view = {
                        'id': '{form_id}_markup'.format(form_id=form_id),
                        'content': tree_elem,
                        'filename': form_view['filename']
                    }

                if markup_view is None:
                    print('Warning: markup view with id = "%s" not found; skipped' % markup_id)
                    continue

                message['markup'] = MarkupManager.parse_markup(markup_view, translator_func, form_params, l10n_params)

        if 'markup' in message and 'screen' not in message:
            print('Warning: messages can not contain markups without screens attached to them; skipped')
            return None

        if len(message.keys()) < 1:
            print('Warning: empty message; skipped')
            return None

        return {
            'id': form_id,
            'message': message
        }

