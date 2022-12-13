

class ButtonManager:
    def parse_button(self, button_view, arg_splitter=','):
        btn_elem = button_view['content']
        btn_id = button_view['id']

        args_str = btn_elem.attrib.get('args')
        args = []

        if args_str is not None:
            btn_args = args_str.split(arg_splitter)

            for index, btn_arg in enumerate(btn_args):
                if btn_arg is not None and len(btn_arg) > 0:
                    if len(btn_arg) > 1 and btn_arg[0] == ':':
                        args.append( btn_arg[1:] )
                    elif btn_arg[0] != ':':
                        args.append( btn_arg )

        visibility_condition = btn_elem.attrib.get('show-if')
        mask = btn_elem.attrib.get('mask')

        return {
            'id': btn_id,
            'args': args,
            'visibility_condition': visibility_condition,
            'mask': mask
        }






