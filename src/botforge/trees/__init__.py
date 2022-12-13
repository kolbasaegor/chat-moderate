from botforge import Forms


class Trees:
    """
    User session aware state manager.
    """

    class Events:
        on_state_entered = 'on_state_entered'
        on_state_left = 'on_state_left'
        on_state_repeated = 'on_state_repeated'

    class Intents:
        get_state_entry_params = 'get_state_entry_params'

    def __init__(self, view_manager, user_session, catcher, argument_resolvers):
        self._view_manager = view_manager
        self._user_session = user_session
        self._catcher = catcher
        self._argument_resolvers = argument_resolvers

    # state management

    @staticmethod
    def _default_on_state_left_event_handler(old_tree_id: str, old_state_id: str, new_tree_id: str, new_state_id: str):
        print('Tree state has been left; old_tree_id = %s, old_state_id = %s, new_tree_id = %s, new_state_id = %s' %
              (old_tree_id, old_state_id, new_tree_id, new_state_id))

    @staticmethod
    def _default_on_state_repeated_event_handler(forms, from_user_id, state_id, form_params, l10n_params,
                                                 last_message_id):
        forms.update_form(from_user_id, last_message_id, state_id, form_params, l10n_params)

    @staticmethod
    def _default_on_state_entered_event_handler(new_state_id: str, form_params: dict, l10n_params: dict,
                                                forms: Forms, from_user_id):
        forms.send_form(from_user_id, new_state_id, form_params, l10n_params)

    @staticmethod
    def _default_get_state_entry_params_intent_handler(tree_id: str, state_id: str):
        return {'form_params': {}, 'l10n_params': {}}

    def go_to(self, tree_id: str, state_id: str, reenter=False):
        old_tree_id = self._user_session.get('tree_id')
        old_state_id = self._user_session.get('state_id')

        new_get_state_entry_params_intent_handler = self._catcher \
            .get_tree_intent_handler(intent_type=Trees.Intents.get_state_entry_params,
                                     tree_id=tree_id, state_id=state_id)

        if new_get_state_entry_params_intent_handler is None:
            new_get_state_entry_params_intent_handler = \
                self._catcher.pack_handler(Trees._default_get_state_entry_params_intent_handler, None)

        if old_tree_id == tree_id and old_state_id == state_id and reenter is False:
            # state was REPEATED, but not entered/left

            intent_argument_resolvers = {
                'tree_id': tree_id,
                'state_id': state_id,
                **self._argument_resolvers
            }

            new_state_entry_params = self._catcher.execute(new_get_state_entry_params_intent_handler,
                                                           intent_argument_resolvers)

            on_state_repeated_event_handler = self._catcher \
                .get_tree_event_handler(event_type=Trees.Events.on_state_repeated,
                                        tree_id=tree_id, state_id=state_id)

            if on_state_repeated_event_handler is None:
                print('Warning: could not find the repeated event handler for the following state: tree_id = %s, state_id = %s' %
                      (tree_id, state_id), flush=True)

                on_state_repeated_event_handler = \
                    self._catcher.pack_handler(Trees._default_on_state_repeated_event_handler, None)

            event_argument_resolvers = {
                'tree_id': tree_id,
                'state_id': state_id,
                'form_params': new_state_entry_params.get('form_params'),
                'l10n_params': new_state_entry_params.get('l10n_params'),
                **self._argument_resolvers
            }

            self._catcher.execute(on_state_repeated_event_handler, event_argument_resolvers)
        else:
            old_on_state_left_event_handler = self._catcher\
                .get_tree_event_handler(event_type=Trees.Events.on_state_left,
                                        tree_id=old_tree_id, state_id=old_state_id)

            if old_on_state_left_event_handler is None:
                print('Warning: could not find the old state left event handler: old_tree_id = %s, old_state_id = %s' %
                      (old_tree_id, old_state_id), flush=True)
                old_on_state_left_event_handler = \
                    self._catcher.pack_handler(Trees._default_on_state_left_event_handler, None)

            new_on_state_entered_event_handler = self._catcher\
                .get_tree_event_handler(event_type=Trees.Events.on_state_entered,
                                        tree_id=tree_id, state_id=state_id)

            if new_on_state_entered_event_handler is None:
                print('Warning: could not find the new state entered event handler: tree_id = %s, state_id = %s' %
                      (tree_id, state_id), flush=True)
                new_on_state_entered_event_handler = \
                    self._catcher.pack_handler(Trees._default_on_state_entered_event_handler, None)

            # switch the state

            self._user_session['tree_id'] = tree_id
            self._user_session['state_id'] = state_id

            event_argument_resolvers = {
                'old_tree_id': old_tree_id,
                'old_state_id': old_state_id,
                'new_tree_id': tree_id,
                'new_state_id': state_id,
                **self._argument_resolvers
            }

            # leave old state handler

            self._catcher.execute(old_on_state_left_event_handler, event_argument_resolvers)

            # get params for state transition

            intent_argument_resolvers = {
                'tree_id': tree_id,
                'state_id': state_id,
                **self._argument_resolvers
            }

            new_state_entry_params = self._catcher.execute(new_get_state_entry_params_intent_handler,
                                                           intent_argument_resolvers)

            event_argument_resolvers = {
                'old_tree_id': old_tree_id,
                'old_state_id': old_state_id,
                'new_tree_id': tree_id,
                'new_state_id': state_id,
                'form_params': new_state_entry_params.get('form_params'),
                'l10n_params': new_state_entry_params.get('l10n_params'),
                **self._argument_resolvers
            }

            # new state entry handler
            self._catcher.execute(new_on_state_entered_event_handler, event_argument_resolvers)

    def go_back(self):
        # no parameters needed - they are retrieved on on_enter call of the state
        tree_id = self._user_session['tree_id']
        state_id = self._user_session['state_id']

        current_tree = self._view_manager.get_tree(tree_id)
        current_state_node = current_tree['flat_tree'].get(state_id)

        if current_state_node is None:
            print('Error: current state node is not found: tree_id = %s, state_id = %s' % (tree_id, state_id))
            return False

        prev_state_node = current_tree['flat_tree'].get(current_state_node.get('prev_state_id'))

        if prev_state_node is None:
            print('Error: prev state node is not found: tree_id = %s, state_id = %s' % (tree_id, state_id))
            return False

        return self.go_to(tree_id, prev_state_node.get('id'))

    def go_forward(self):
        # no parameters needed - they are retrieved on on_enter call of the state
        tree_id = self._user_session['tree_id']
        state_id = self._user_session['state_id']

        current_tree = self._view_manager.get_tree(tree_id)
        current_state_node = current_tree['flat_tree'].get(state_id)

        if current_state_node is None:
            print('Error: current state node is not found: tree_id = %s, state_id = %s' % (tree_id, state_id))
            return False

        next_state_node = current_tree['flat_tree'].get(current_state_node.get('next_state_id'))

        if next_state_node is None:
            print('Error: next state node is not found: tree_id = %s, state_id = %s' % (tree_id, state_id))
            return False

        return self.go_to(tree_id, next_state_node.get('id'))

    # TODO: go_to_root

    def repeat(self, reenter=False):
        tree_id = self._user_session['tree_id']
        state_id = self._user_session['state_id']

        return self.go_to(tree_id, state_id, reenter)

