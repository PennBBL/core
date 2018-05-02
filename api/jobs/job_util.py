"""
Job related utilities.
"""
from ..auth import has_access
from ..dao.basecontainerstorage import ContainerStorage
from ..dao.containerutil import singularize

def get_context_for_destination(cont_type, cont_id, uid, storage=None, cont=None):
    """ Get gear run context for the given destination container.
    
    Arguments:
        cont_type (str): The destination container type.
        cont_id (str): The destination container id.
        uid (str): The user id for permission checking.
        storage (ContainerStorage): The optional container storage instance.
        cont (dict): The optional container, if already found.

    Returns:
        dict: The context built from the container hierarchy
    """
    if not storage:
        storage = ContainerStorage.factory(cont_type)

    if not cont:
        cont = storage.get_container(cont_id)

    cont['cont_type'] = storage.cont_name
    parent_tree = storage.get_parent_tree(cont_id, cont=cont)

    # This is a quick and dirty solution that walks top down, updating
    # context from each parent container if the user has ro permissions.
    context = {}

    # Walk top down, updating context as we go
    parent_tree.reverse()
    parent_tree.append(cont)

    for parent in parent_tree:
        if not uid or has_access(uid, parent, 'ro'):
            cont_type = singularize(parent['cont_type'])
            parent_context = parent.get('info', {}).get('context', {})

            for key, value in parent_context.items():
                context[key] = {
                    'container_type': cont_type,
                    'label': parent['label'],
                    'id': parent['_id'],
                    'value': value
                }

    return context

def resolve_context_inputs(config, gear, cont_type, cont_id, uid, context=None):
    """ Resolve input fields with a base of 'context' given a destination and gear spec.
    
    Arguments:
        config (dict): The job configuration to be updated
        gear (dict): The gear spec
        cont_type (str): The destination container type.
        cont_id (str): The destination container id.
        uid (str): The user id for permission checking
        context (dict): The optional context, if already resolved
    """
    # Callers don't (shouldn't) specify the context inputs when scheduling a job,
    # so we walk the gear inputs, checking for any context inputs.
    for x in gear['gear']['inputs']:
        input_type = gear['gear']['inputs'][x]['base']
        if input_type == 'context':
            # Lazily resolve the context a single time
            if context is None:
                context = get_context_for_destination(cont_type, cont_id, uid)

            if x in context:
                config['inputs'][x] = {
                    'base': 'context',
                    'found': True,
                    'value': context[x]['value']
                }
            else:
                config['inputs'][x] = {
                    'base': 'context',
                    'found': False
                }

