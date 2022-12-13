

class TreeManager:
    @staticmethod
    def parse_tree(tree_view, all_views, **kwargs):
        tree_root = tree_view['content']
        tree_id = tree_view['id']

        if tree_root.tag != 'tree':
            print("Error: could not parse tree_id = %s; tree's root element should be a tree" % tree_id, flush=True)
            return None

        flat_tree = {}

        def parse_subtree(tree):
            if len(tree) < 1:
                # tree has no children
                return []

            children = []

            for node in tree:
                if node.tag != 'state':
                    print('Warning: unsupported tree node type - tree_id = %s, node tag = %s' % (tree_id, node.tag))
                    continue

                state_id = node.attrib.get('id')

                if state_id is None:
                    print('Warning: could not parse state node - no state id provided; tree_id = %s; node skipped' %
                          tree_id)
                    continue

                form_id = node.attrib.get('form_id')

                if form_id is None:
                    # by default, if form_id is not provided, we set it to be equal to state id
                    form_id = state_id

                if form_id not in all_views['forms'].keys():
                    print('Warning: could not find the form specified - form_id = %s; node skipped' % form_id)
                    continue

                node_children = parse_subtree(node)

                next_state_id = node.attrib.get('next')

                if next_state_id is None:
                    if len(node_children) == 1:
                        # by default, if a state node has the only child, we set it to be the next state
                        next_state_id = node_children[0]['id']

                if tree.tag == 'tree':
                    # if root elem - prev_state_id is None
                    prev_state_id = None
                else:
                    # otherwise, it is equal to the id of the parent node
                    prev_state_id = tree.attrib.get('id')

                state = {
                    'id': state_id,
                    'form_id': form_id,
                    'next_state_id': next_state_id,
                    'prev_state_id': prev_state_id,
                    'children': node_children,
                    'handlers': []
                }

                flat_tree[state_id] = state
                children.append(state)

            return children

        return {
            'id': tree_id,
            'tree': parse_subtree(tree_root),
            'flat_tree': flat_tree,
        }

