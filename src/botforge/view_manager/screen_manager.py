import re


class ScreenManager:

    @staticmethod
    def parse_screen(screen_view, translator_func, screen_params: dict = None, l10n_params: dict = None, **kwargs):
        # preparations

        tree_root = screen_view['content']
        screen_id = screen_view['id']

        def should_skip_tag_parsing(dom_elem, screen_params):
            if dom_elem.attrib.get('item') is None:
                print(
                    'Warning: attribute "item" not found in "for" tag in screen "%s". Skipping the tag' % screen_id)
                return True

            if dom_elem.attrib.get('from') is None:
                print(
                    'Warning: attribute "from" not found in "for" tag in screen "%s". Skipping the tag' % screen_id)
                return True

            if dom_elem.attrib.get('delimiter') is None:
                print(
                    'Warning: attribute "delimiter" not found in "for" tag in screen "%s". Skipping the tag' % screen_id)
                return True

            if screen_params.get(dom_elem.attrib.get('from')) is None:
                print(
                    'Warning: one of attributes, required by "for" cycle instruction was not supplied to the'
                    ' templater in screen "%s". Skipping the tag' % screen_id)
                return True

            condition_var_name = dom_elem.attrib.get('show-if')

            # check if we have a visibility condition
            if condition_var_name is not None:
                if len(condition_var_name) > 0 and condition_var_name[0] == ':':
                    condition_var_name = condition_var_name[1:]

                condition_is_inverted = condition_var_name[0] == '!'

                if condition_is_inverted:
                    condition_var_name = condition_var_name[1:]

                condition_var_val = screen_params.get(condition_var_name)

                if condition_var_val is None:
                    print('Warning: no argument value provided for the "show-if" attribute of one of "for" tags of '
                          'the screen "%s"; skipping the tag' % screen_id, flush=True)
                    return True

                if condition_var_val in [None, False]:
                    # btn does not satisfy the condition
                    if not condition_is_inverted:
                        return True
                    else:
                        # just go on
                        pass
                else:
                    if condition_is_inverted:
                        # not satisfies because it is inverted
                        return True

            return False

        # parsing

        if tree_root.tag == 'screen':
            screen_text = tree_root.text

            for dom_elem in tree_root:
                if dom_elem.tag == 'for':
                    should_skip_tag_contents = should_skip_tag_parsing(dom_elem, screen_params)

                    if not should_skip_tag_contents:
                        for_text = ScreenManager.parse_for(dom_elem, screen_params)

                        template_cycle_obj_occurrences = ScreenManager.get_template_cycle_obj_occurrences(
                            dom_elem.attrib['item'], for_text)

                        templatized_objects = []

                        # go through all the collection objects
                        for obj in screen_params.get(dom_elem.attrib.get('from')):
                            templatized_objects.append(
                                ScreenManager.templatize_cycle_object(obj, for_text, template_cycle_obj_occurrences))

                        delimiter = dom_elem.attrib.get('delimiter').encode('utf-8').decode('unicode_escape')

                        screen_text += delimiter.join(templatized_objects)

                    # anyways - add the tail after the tag
                    text_to_add = dom_elem.tail if dom_elem.tail is not None else ''

                    if should_skip_tag_contents:
                        text_to_add = text_to_add.lstrip()

                    screen_text += text_to_add
                else:
                    screen_text += ScreenManager.parse_format_tag(dom_elem, screen_params)

            # get all the screen params object keys
            template_obj_occurrences = ScreenManager.get_template_obj_occurrences(screen_text)
            screen_text = ScreenManager.templatize_text(screen_params, screen_text, template_obj_occurrences)

            screen_text = '\n'.join([l.lstrip() for l in screen_text.split('\n')]).rstrip()

            l10n_entries = ScreenManager.get_l10n_entries(screen_text)

            for entry in l10n_entries:
                # TODO: release the whole text formation
                screen_text = screen_text.replace('{%s}' % entry, translator_func(entry, **l10n_params))

            return screen_text

        print('Warning: no screen "%s" found' % screen_id)
        return '{no screen "%s" found}' % screen_id

    @staticmethod
    def get_template_cycle_obj_occurrences(object_id, text):
        regex_template = r'(\[% ' + re.escape(object_id) + r'(?:\.?\w+){0,} %\])'
        return re.findall(regex_template, text)

    @staticmethod
    def templatize_cycle_object(obj, text, occurrences):
        for occurrence in occurrences:
            try:
                obj_path = occurrence.replace(' %]', '').replace('[% ', '').split('.')
                replacement = occurrence  # what we're replacing the template for

                if len(obj_path) > 1:
                    obj_path = obj_path[1:]

                if len(obj_path) < 2:
                    replacement = str(obj.get(obj_path[0], occurrence))
                elif len(obj_path) == 2:
                    replacement = str(obj.get(obj_path[0], {}).get(obj_path[1], occurrence))
                elif len(obj_path) == 3:
                    replacement = str(obj.get(obj_path[0], {}).get(obj_path[1], {}).get(obj_path[2], occurrence))

                text = text.replace(occurrence, replacement)
            except Exception as e:
                pass

        return text

    @staticmethod
    def get_template_obj_occurrences(text):
        regex_template = r'(\[% :[\w\._]{1,} %\])'
        return re.findall(regex_template, text)

    @staticmethod
    def templatize_text(obj, text, occurrences):
        for occurrence in occurrences:
            try:
                obj_path = occurrence.replace(' %]', '').replace('[% :', '').split('.')
                replacement = occurrence

                if len(obj_path) < 2:
                    replacement = str(obj.get(obj_path[0], occurrence))
                elif len(obj_path) == 2:
                    replacement = str(obj.get(obj_path[0], {}).get(obj_path[1], occurrence))
                elif len(obj_path) == 3:
                    replacement = str(obj.get(obj_path[0], {}).get(obj_path[1], {}).get(obj_path[2], occurrence))

                text = text.replace(occurrence, replacement)
            except:
                pass

        return text

    @staticmethod
    def parse_format_tag(elem, screen_params):
        # TODO: parse elements recursively (e.g.: <i><b>Italic Bold</b></i>)

        def should_skip_tag_parsing(elem, screen_params):
            condition_var_name = elem.attrib.get('show-if')

            # check if we have a visibility condition
            if condition_var_name is not None:
                if len(condition_var_name) > 0 and condition_var_name[0] == ':':
                    condition_var_name = condition_var_name[1:]

                condition_is_inverted = condition_var_name[0] == '!'

                if condition_is_inverted:
                    condition_var_name = condition_var_name[1:]

                condition_var_val = screen_params.get(condition_var_name)

                if condition_var_val is None:
                    print('Warning: no argument value provided for the "show-if" attribute of one of format tags of '
                          'the screen screen; skipping the tag', flush=True)
                    return True

                if condition_var_val in [None, False]:
                    # btn does not satisfy the condition
                    if not condition_is_inverted:
                        return True
                    else:
                        # just go on
                        pass
                else:
                    if condition_is_inverted:
                        # not satisfies because it is inverted
                        return True

            return False

        text = ''

        if elem.tag in ['b', 'i', 'a', 'pre', 'code', 'span']:
            should_skip_tag_contents = should_skip_tag_parsing(elem, screen_params)

            if not should_skip_tag_contents:
                if elem.tag == 'span':
                    text += elem.text
                else:
                    if elem.tag == 'a':
                        text += '<%s href="%s">' % (elem.tag, elem.attrib['href'])
                    else:
                        text += '<%s>' % elem.tag

                    text += elem.text
                    text += '</%s>' % elem.tag

            text_to_add = elem.tail if elem.tail is not None else ''

            if should_skip_tag_contents:
                text_to_add = text_to_add.lstrip()

            text += text_to_add

        return text

    @staticmethod
    def parse_for(elem, screen_params):
        text = elem.text

        for child in elem.getchildren():
            text += ScreenManager.parse_format_tag(child, screen_params)

        return '\n'.join([l.lstrip() for l in text.replace('\n', '', 1).rstrip().split('\n')])

    @staticmethod
    def get_l10n_entries(text):
        regex_template = r'\{(.*?)\}'
        return re.findall(regex_template, text)

