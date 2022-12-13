from botforge.view_manager import ScreenManager
from botforge.tests import common_stubs


def test_for_cycles():
    test_screen_tree = common_stubs.get_screen_view()
    parsed_screen = ScreenManager.parse_screen(test_screen_tree,
                                               common_stubs.get_translator_func(),
                                               {'range': [1, 2, 3]},
                                               {'test_title': 'Card test title'})
    return parsed_screen


print(test_for_cycles())
