import glob
import importlib.util
import os
from typing import List


def get_directory_filenames(path: str, extensions: List[str]):
    result = []

    for extension in extensions:
        for filename in glob.iglob('{path}/**/*.{extension}'.format(path=path,
                                                                    extension=extension),
                                   recursive=True):
            result.append(filename)

    return result


def env(key, default=None):
    return os.environ.get(key, default)


def import_module(path, name=None):
    if name is None:
        name = ''

    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # mod = importlib.import_module(name)

    # components = name.split('.')
    #
    # for comp in components[1:]:
    #     mod = getattr(mod, comp)

    return mod


def get_directories_names(path):
    if not os.path.exists(path):
        # no modules
        return []

    return [name for name in os.listdir(path)
            if os.path.isdir('{path}{path_separator}{dir}'.format(path=path, dir=name,
                                                                  path_separator=os.path.sep))]


def escape_html(text):
    if text is None:
        return None

    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

