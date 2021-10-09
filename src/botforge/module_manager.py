import json
# import yaml
import os
from xml.etree import ElementTree

from botforge.utils import import_module, get_directory_filenames
from botforge.utils.validators.l10n import is_l10n_valid
from botforge.utils.validators.module import is_module_content_valid
from botforge.utils.validators.package import is_package_valid
from botforge.utils.validators.views import is_views_content_valid


class ModuleManager:
    @staticmethod
    def _load_package(path_to_module: str):
        path_to_package = os.path.join(path_to_module, 'package.json')

        # TODO: catch exceptions
        package = json.loads(open(path_to_package, encoding='utf-8').read())

        if not is_package_valid(package):
            # TODO: react on not valid package loading
            return None

        return package

    @staticmethod
    def _load_module_content(path_to_module: str, name: str):
        path_to_module = os.path.join(path_to_module, 'module.py')

        module_content = import_module(path_to_module, name)

        if not is_module_content_valid(module_content):
            # TODO: react on invalid module content
            return None

        return module_content

    # resources

    @staticmethod
    def _get_basename(filename: str):
        """ Take filename without file extension """
        return os.path.splitext(os.path.basename(filename))[0]

    @staticmethod
    def _extract_subviews(root_view, subviews_names):
        tags_to_check = [root_view]
        result = []

        while len(tags_to_check) > 0:
            current_tag = tags_to_check.pop(0)

            if current_tag.tag in subviews_names:
                result.append(current_tag)

            child_tags = [tag for tag in current_tag]
            tags_to_check.extend(child_tags)

        return result

    @staticmethod
    def _load_views(path_to_module: str):
        path_to_views = os.path.join(path_to_module, 'views')

        path_to_screens = os.path.join(path_to_views, 'screens')
        path_to_markups = os.path.join(path_to_views, 'markups')
        path_to_forms = os.path.join(path_to_views, 'forms')
        path_to_trees = os.path.join(path_to_views, 'trees')

        # parse views

        views_filenames = get_directory_filenames(path_to_views, ['html', 'xml'])
        views = dict(screens={}, markups={}, forms={}, trees={},
                     buttons={})

        for filename in views_filenames:
            # parse xml

            view_text = open(filename, encoding='utf-8').read()

            xml_parser = ElementTree.XMLParser()
            xml_parser.feed(view_text)
            tree_root = xml_parser.close()

            view_id = tree_root.attrib.get('id', None)

            if view_id is None:
                print('Warning: no id attribute specified for view "%s"; skipped' % filename)
                continue

            view_type = None

            if filename.startswith(path_to_markups):
                view_type = 'markups'
            elif filename.startswith(path_to_screens):
                view_type = 'screens'
            elif filename.startswith(path_to_forms):
                view_type = 'forms'
            elif filename.startswith(path_to_trees):
                view_type = 'trees'

            if view_type is None:
                print('Error: unknown view type: view_id = %s' % view_id)
                continue

            if view_type == 'forms':
                subviews = ModuleManager._extract_subviews(tree_root, ['markup', 'inline-markup', 'screen'])

                for subview in subviews:
                    subview_tag = subview.tag

                    count = 0
                    new_subview_id_base = '{form_id}_{tag}'.format(form_id=view_id, tag=subview_tag)
                    new_subview_id = '{base}_{count}'.format(base=new_subview_id_base, count=count)

                    subview_type = None

                    if subview_tag in ['markup', 'inline-markup']:
                        subview_type = 'markups'
                    elif subview_tag in ['screen']:
                        subview_type = 'screens'

                    if subview_type is None:
                        print('Warning: subview type is not supported - %s; skipped' % subview_type, flush=True)
                        continue

                    while views.get(subview_type, {}).get(new_subview_id) is not None:
                        count += 1
                        new_subview_id_base = '{form_id}_{tag}'.format(form_id=view_id, tag=subview_tag)
                        new_subview_id = '{base}_{count}'.format(base=new_subview_id_base, count=count)

                    views[subview_type][new_subview_id] = {
                        'filename': filename,
                        'content': subview,
                        'id': new_subview_id,
                        'form_id': view_id
                    }

            views[view_type][view_id] = {
                'filename': filename,
                'content': tree_root,
                'id': view_id
            }

            if view_type in ['screens', 'markups']:
                views[view_type][view_id]['form_id'] = '*'  # so for any screen/markup that has no parent form

        # parse buttons from markups

        for markup_view in views.get('markups').values():
            form_id = markup_view['form_id']
            markup_id = markup_view['id']
            markup_filename = markup_view['filename']
            markup_type = markup_view['content'].tag

            tags_to_check = [markup_view['content']]

            # traverse the whole markup tree

            while len(tags_to_check) > 0:
                current_tag = tags_to_check.pop(0)

                if current_tag is None:
                    continue

                if current_tag.tag == 'button' and 'id' in current_tag.attrib:
                    btn_id = current_tag.attrib.get('id')

                    btn_key = '{form_id}_{btn_id}'.format(form_id=form_id, btn_id=btn_id)

                    # within the boundaries of a single form buttons should have the same signatures (args and etc.)

                    views['buttons'][btn_key] = {
                        'id': btn_id,
                        'filename': markup_filename,
                        'content': current_tag,
                        'markup_type': markup_type,
                        'form_id': form_id,
                        'markup_id': markup_id,
                    }
                    continue

                child_tags = [tag for tag in current_tag]
                tags_to_check.extend(child_tags)

        if not is_views_content_valid(views):
            print('Error: views content is not valid', flush=True)
            return None

        return views

    @staticmethod
    def _load_l10n(path_to_module: str):
        path_to_l10n = os.path.join(path_to_module, 'l10n')

        l10n_filenames = get_directory_filenames(path_to_l10n, ['json', 'yml', 'yaml'])
        l10ns = dict()

        for filename in l10n_filenames:
            # TODO: separately parse json & yaml

            l10n_tree = None

            if filename.endswith('json'):
                # json file
                l10n_tree = json.load(open(filename, encoding='utf-8'))
            else:
                # yaml file
                # IMPORTANT: DOES NOT SUPPORT emoji & other unicode symbols in contents
                # TODO: enable yaml
                # l10n_tree = yaml.load(open(filename, encoding='utf-8'))
                pass

            for l10n_id in l10n_tree.keys():
                if l10n_id in l10ns.keys():
                    print('Warning: duplicate l10n entry id: "%s" in file "%s"; skipped' % (l10n_id, filename))
                    continue

                l10ns[l10n_id] = {
                    'filename': filename,
                    'content': l10n_tree[l10n_id],
                    'id': l10n_id
                }

        if not is_l10n_valid(l10ns):
            # TODO: react on invalid data
            return None

        return l10ns

    # --------- resources ----------

    @staticmethod
    def load_module(path_to_module: str, name:str = None):
        """
        Load the module under the path given.
        The path should contain the following things:

        - package.json(required)
        - module.py(required)
            * contains 'entry' method, accepting Bot instance and returning ... nothing
        - entry.py(optional)
        - views folder(optional)
        - views/markups(optional)
        - views/screens(optional)
        - l10n(optional)
        - src(optional)

        Single module contains the following things:

            - content: python content of the module(module.py)
            - package: dict with configuration of the module(package.json)
            - views: a dict, consisting of the following dicts;
                - markups: a dict of contents of markup files; key is the name of the markup
                - screens: a dict of contents of screen files; key is the name of the screen
            - l10n: a dict, consisting of contents of l10n files; key is the name of the l10n item

        :param name: name of the module at runtime
        :param path_to_module: path to the module
        :return: loaded module instance
        """
        package = ModuleManager._load_package(path_to_module)
        module_content = ModuleManager._load_module_content(path_to_module, name)
        views = ModuleManager._load_views(path_to_module)
        l10n = ModuleManager._load_l10n(path_to_module)

        # check if required components are set
        if None in [package, module_content]:
            # TODO: react on invalid package or module
            pass

        module = dict(content=module_content,
                      package=package,
                      views=views,
                      l10n=l10n)

        return module

