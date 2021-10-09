class L10n(object):
    ANY_LANGUAGE_MASK = '*'

    def __init__(self, modules: dict):
        self._modules = modules
        self._translations = dict()

        for module_id in modules.keys():
            for l10n_id in modules[module_id]['l10n'].keys():
                if l10n_id in self._translations.keys():
                    print('Warning: duplicate l10n entry id: "%s" in file "%s"; skipped' % (l10n_id,
                                                                                            modules[module_id]['l10n'][
                                                                                                l10n_id]['filename']))
                    continue

                self._translations[l10n_id] = modules[module_id]['l10n'][l10n_id]['content']

    def translator(self, lang: str):
        def translate(key: str, **kwargs):
            default_result = '{%s[%s]}' % (key, lang)

            best_fitting_translation_ids = [tid for tid in self._translations.keys() if key in tid]

            if len(best_fitting_translation_ids) < 1:
                print('Error: there is no such a translation: "%s"' % key)
                return default_result

            translation_pair = self._translations.get(key)

            if translation_pair is None:
                print('Error: there is no such a translation: "%s"' % key)
                return default_result

            translation_value = translation_pair.get(lang, translation_pair.get(L10n.ANY_LANGUAGE_MASK))

            if translation_value is None:
                print('Error: there is no such a translation: "%s"' % key)
                return default_result

            try:
                return translation_value.format(**kwargs)
            except KeyError:
                print('Warning: not enough parameters for translation of "%s" key' % key)
                return default_result

        return translate
