from .pipeline import PipelineStage
from ..util import filtered_container_list, file_filter_to_regex, nil_value, is_nil

def pop_collection(cont, key):
    """Nested pop of key from container.

    This will perform a nested extraction of key from cont, popping it from the deepest level.

    Arguments:
        cont (dict): The container to query
        key (str): A dot(.) separated string containing the key to pop

    Returns:
        list: The popped value, or an empty list
    """
    result = []
    parts = key.split('.')

    for part in parts[:-1]:
        cont = cont.get(part)
        if not cont:
            break

    if cont and not is_nil(cont):
        result = cont.pop(parts[-1], [])

    return result

class MatchContainers(PipelineStage):
    """Extracts a list of containers from each row, producing a row for each matched container.

    Expects a single payload which is a list of rows generated from the Aggregate stage.
    Emits a list of rows, which have been unwound for each container matched. 
    If no match was found, then the original row will be included at the end of the list of rows.
    """
    def __init__(self, collection_key, output_key, filters, match_type):
        """Initialize this pipeline stage.

        Arguments:
            collection_key (str): The key of the collection to unwind.
            output_key (str): The key of the destination field where unwound values should be placed.
            filters (dict): The filter that should be applied to the name or label value
            match_type (str): The match type to perform, one of: all, newest, oldest, first, last
        """
        super(MatchContainers, self).__init__()

        self.collection_key = collection_key
        self.output_key = output_key
        
        # Compile filters
        self.filters = []
        for name, filter_spec in filters:
            pattern = file_filter_to_regex(filter_spec)
            self.filters.append((name, pattern))

        self.match_type = match_type

    def process(self, payload):
        # Keep unmatched values at the end
        rows = []
        unmatched = []

        # Pop and filter the containers from payload
        for row in payload:
            containers = pop_collection(row, self.collection_key)
            containers = filtered_container_list(containers, self.filters, self.match_type)

            if containers:
                # Emit one row per match
                for entry in containers:
                    new_row = row.copy()
                    new_row[self.output_key] = entry 
                    rows.append(new_row)
            else:
                new_row = row.copy()
                new_row[self.output_key] = nil_value
                unmatched.append(new_row)

        self.emit(rows + unmatched)

