from botforge import L10n
from botforge.view_manager.button_manager import ButtonManager
from botforge.view_manager.form_manager import FormManager
from botforge.view_manager.markup_manager import MarkupManager
from botforge.view_manager.screen_manager import ScreenManager
from botforge.view_manager.tree_manager import TreeManager


class ViewManager:
    def __init__(self, modules: dict, l10n: L10n):
        self._modules = modules
        self._views = dict(screens={}, markups={}, forms={}, trees={},
                           buttons={})
        self._l10n = l10n

        self._screen_manager = ScreenManager()
        self._markup_manager = MarkupManager()
        self._form_manager = FormManager()
        self._tree_manager = TreeManager()
        self._button_manager = ButtonManager()

        for module_id in modules.keys():
            for view_type in modules[module_id]['views'].keys():
                for view_key in modules[module_id]['views'][view_type].keys():
                    if view_key in self._views[view_type]:
                        print('Warning: duplicate view id "%s" in file "%s"; skipped' % (
                            view_key, modules[module_id]['views'][view_key]['filename']))
                        continue

                    self._views[view_type][view_key] = modules[module_id]['views'][view_type][view_key]

    # helper getters

    def get_translator(self, lang: str):
        return self._l10n.translator(lang)

    # bunch getters for views

    def get_all_views(self):
        return self._views

    def get_screen_views(self):
        return self._views.get('screens', {})

    def get_markup_views(self):
        return self._views.get('markups', {})

    def get_form_views(self):
        return self._views.get('forms', {})

    def get_tree_views(self):
        return self._views.get('trees', {})

    def get_button_view(self):
        return self._views.get('buttons', {})

    # individual getters for views

    def get_view(self, view_id: str, lang: str, **view_params):
        # print('>> WARNING: Deprecated method. Please, use get_screen(..) and get_markup(..) methods instead')

        if view_id not in self._views['markups'].keys() and view_id not in self._views['screens'].keys():
            print('Error: there is no such a view: "%s" ' % view_id)
            return None

        if view_id in self._views['markups']:
            return self.get_markup(view_id, lang, view_params.get('markup_params', {}))

        if view_id in self._views['screens']:
            return self.get_screen(view_id, lang, view_params.get('screen_params', {}),
                                   view_params.get('l10n_params', {}))

        if view_id in self._views['forms']:
            return self.get_form(view_id, lang, view_params.get('form_params', {}), view_params.get('l10n_params', {}))

        if view_id in self._views['trees']:
            return self.get_form(view_id, lang, view_params.get('tree_params', {}), view_params.get('l10n_params', {}))

    def get_screen(self, screen_id: str, lang: str, screen_params: dict = None, l10n_params: dict = None, **kwargs):
        if screen_id not in self._views['screens'].keys():
            print('Error: there is no such a screen: %s' % screen_id)
            return None

        if l10n_params is None:
            l10n_params = {}

        if screen_params is None:
            screen_params = {}

        translator_func = self._l10n.translator(lang)  # for translating markup l10n entries
        screen_view = self._views['screens'][screen_id]

        return self._screen_manager.parse_screen(screen_view, translator_func, screen_params, l10n_params)

    def get_markup(self, markup_id: str, lang: str, markup_params: dict = None, l10n_params: dict = None, **kwargs):
        if markup_id not in self._views['markups'].keys():
            print('Error: there is no such a markup: %s' % markup_id)
            return None

        if l10n_params is None:
            l10n_params = {}

        if markup_params is None:
            markup_params = {}

        translator_func = self._l10n.translator(lang)  # for translating markup l10n entries
        markup_view = self._views['markups'][markup_id]

        return self._markup_manager.parse_markup(markup_view, translator_func, markup_params, l10n_params)

    def get_form(self, form_id: str, lang: str, form_params: dict = None, l10n_params: dict = None, **kwargs):
        """ Once it might happen that we will need to pass parameters to different screens/markups,
        involved in formation of the form.  In that case, we could adopt a new parameter for this function that would
        capture parameter resolvers, packed by element type (screen/markup/etc) and the id of the element."""
        if form_id not in self._views['forms'].keys():
            print('Error: there is no such a form: %s' % form_id)
            return None

        if form_params is None:
            form_params = {}

        if l10n_params is None:
            l10n_params = {}

        translator_func = self._l10n.translator(lang)
        form_view = self._views['forms'][form_id]

        return self._form_manager.parse_form(form_view, self._views, translator_func, form_params, l10n_params)

    def get_tree(self, tree_id: str):
        if tree_id not in self._views['trees'].keys():
            print('Error: there is no such a tree: %s' % tree_id)
            return None

        tree_view = self._views['trees'][tree_id]

        return self._tree_manager.parse_tree(tree_view, self._views)

    def get_button(self, form_id: str = '*', button_id: str = None):
        if button_id is None:
            print('Error: button id has not been provided', flush=True)
            return None

        btn_view_key = '{form_id}_{btn_id}'.format(form_id=form_id, btn_id=button_id)

        if btn_view_key not in self._views['buttons'].keys():
            print('Error: there is no such a button %s in the form %s' % (button_id, form_id))
            return None

        button_view = self._views['buttons'][btn_view_key]

        return self._button_manager.parse_button(button_view, MarkupManager.TEMPLATE_ARGUMENT_SPLITTER)

    def resolve_button_args(self, form_id: str = '*', button_id: str = None, data: str = None):
        if None in [button_id, data]:
            print('Error: button_id, data and argument_resolvers must be specified', flush=True)
            return dict()

        button = self.get_button(form_id=form_id, button_id=button_id)

        if button is None:
            return dict()

        arg_keys = button['args']
        arg_values = data.split(MarkupManager.DATA_ARGUMENT_SPLITTER)[1:]

        if None in [arg_keys, arg_values] or len(arg_keys) < 1 or len(arg_values) < 1 or len(arg_keys) != len(arg_values):
            print('Error: not enough arguments for button %s' % button_id)
            return dict()

        resolved_btn_args = dict(zip(arg_keys, arg_values))

        return resolved_btn_args
