from botforge.view_manager import MarkupManager
from botforge.tests import common_stubs


def test_markup():
    test_markup_tree = common_stubs.get_markup_view()
    parsed_markup = MarkupManager.parse_markup(test_markup_tree,
                                               common_stubs.get_translator_func(),
                                               {'column': [{'title': '4'}, {'title': '5'}, {'title': '6'}],
                                                'row': [{'title': '1'}, {'title': '2'}, {'title': '3'}]})
    return parsed_markup


def test_inline_markup():
    test_inline_markup_tree = common_stubs.get_inline_markup_view()
    parsed_markup = MarkupManager.parse_markup(test_inline_markup_tree,
                                               common_stubs.get_translator_func(),
                                               {'column': [{'title': '4'}, {'title': '5'}, {'title': '6'}],
                                                'row': [{'title': '1'}, {'title': '2'}, {'title': '3'}]})
    return parsed_markup


markup = test_markup()

print('markup:\n')
for row in markup.keyboard:
    rw = ''

    for btn in row:
        rw += str(btn.__dict__)

    print(rw)

inline_markup = test_inline_markup()

print('\n\ninline markup:\n')
for row in inline_markup.inline_keyboard:
    rw = ''

    for btn in row:
        rw += str(btn.__dict__)

    print(rw)

