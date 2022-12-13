from botforge.view_manager import FormManager
from botforge.tests import common_stubs


def test_form():
    all_views = {
        'markups': {
            'test_markup': common_stubs.get_markup_view(),
        },
        'screens': {
            'test_screen': common_stubs.get_screen_view(),
        }
    }
    test_form = common_stubs.get_form_view()
    parsed_form = FormManager.parse_form(test_form, all_views, common_stubs.get_translator_func(),
                                           {'column': [{'title': '4'}, {'title': '5'}, {'title': '6'}],
                                            'row': [{'title': '1'}, {'title': '2'}, {'title': '3'}],
                                            'range': [1, 2, 4]},
                                           {'test_title': 'TEST TITLE'})
    return parsed_form


form = test_form()

print('id = %s' % form['id'])

for msg in form['messages']:
    print('> message')

    for msg_attr in msg:
        if msg_attr == 'markup':
            print('>> msg attr: %s\n%s' % (msg_attr, str(msg[msg_attr].__dict__)))
        else:
            print('>> msg attr: %s\n%s' % (msg_attr, msg[msg_attr]))

