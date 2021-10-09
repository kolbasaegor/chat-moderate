import json
import os
from collections import OrderedDict
from functools import reduce


def input_till_valid(prompt, validator):
    while True:
        value = input(prompt)

        if validator(value):
            return value
        else:
            print('Wrong value! Please, try again')


def create_package(module):
    return json.dumps(OrderedDict(author=module['author'],
                                  name=module['name'],
                                  version=module['version'],
                                  description=module['description'],
                                  dependencies={}),
                      indent=2
                      )


def create_module(module):
    return '\n'.join([
        'import src.{name}.source'.format(name=module['name']),
        '',
        '',
        'def mount(bot):',
        '    print(\'import {name}\')'.format(name=module['name']),
        '    src.{name}.source.mount(bot)'.format(name=module['name'])
    ])


def create_entry(module):
    return '\n'.join([
        'from botforge import Bot',
        '',
        'bot_token = \'<PUT BOT TOKEN HERE>\'',
        '',
        '',
        'def start():',
        '    bot = Bot(bot_token)',
        '    bot.loop()',
        '',
        'if __name__ == \'__main__\':',
        '    print(\'Bot has successfully started!\')',
        '    start()'
    ])


def create_source(module):
    return '\n'.join([
        'def mount(bot):',
        '    print(\'mounted {name}\')'.format(name=module['name'])
    ])


def create_files(module, dirs):
    open(os.path.join(dirs['root'], 'package.json'), 'w').write(create_package(module))
    open(os.path.join(dirs['root'], 'module.py'), 'w').write(create_module(module))
    open(os.path.join(dirs['root'], 'entry.py'), 'w').write(create_entry(module))

    open(os.path.join(dirs['src'], '__init__.py'), 'w').write('')
    open(os.path.join(dirs['src'], 'source.py'), 'w').write(create_source(module))


def main():
    module = dict(author=input_till_valid('Author name (e.g. "Santa Claus"): ', lambda v: len(v) >= 3),
                  name=input_till_valid('Module name (e.g. "language_switcher"): ', lambda v: len(v) > 1),
                  version=input_till_valid('Version (e.g. 0.0.1): ',
                                           lambda v: v.count('.') == 2 and
                                                     (reduce(lambda c, d: c and d.isdigit(), v.split('.'), True))
                                                     is True),
                  description=input_till_valid('Description (e.g. "Asks a user for his preferred language"): ',
                                               lambda _: True))
    dirs = {
        'root': os.path.join('./', module['name']),

        'buttons': os.path.join('./', module['name'], 'l10n', 'buttons'),
        'messages': os.path.join('./', module['name'], 'l10n', 'messages'),

        'markups': os.path.join('./', module['name'], 'views', 'markups'),
        'screens': os.path.join('./', module['name'], 'views', 'screens'),

        'src': os.path.join('./', module['name'], 'src', module['name']),
    }

    for d in dirs.values():
        if not os.path.exists(d):
            os.makedirs(d)

    create_files(module, dirs)


if __name__ == '__main__':
    # for python 2 compatibility
    try:
        input = raw_input
    except NameError:
        pass

    main()
