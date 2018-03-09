import json
import os
import threading

COLUMN_ALIASES_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'column_aliases.json'))

class ColumnAliases(object):
    """Singleton class that contains the set of known column aliases"""
    __lock = threading.Lock()
    __instance = None

    def __init__(self):
        # Load columns
        with open(COLUMN_ALIASES_FILE, 'r') as f:
            self.columns = json.load(f)

        # Load column map and set default type (string)
        self.column_map = {}
        for col in self.columns:
            if 'group' in col:
                self.column_map[col['name']] = col['group'] 
            elif 'type' not in col:
                col['type'] = 'string'
                self.column_map[col['name']] = (col['src'], col.get('type'))


    @classmethod
    def instance(cls):
        """Get the singleton instance of ColumnAliases"""
        # Double check lock for singleton instance
        if not cls.__instance:
            with cls.__lock:
                if not cls.__instance:
                    cls.__instance = ColumnAliases()

        return cls.__instance

    @classmethod
    def get_columns(cls):
        """Get the full list of column aliases, including type and description"""
        inst = cls.instance()
        return inst.columns

    @classmethod
    def get_column_alias(cls, key):
        """Lookup the alias for the given key.

        Arguments:
            key (str): The column key

        Returns:
            tuple: The aliased (key, datatype), group list, or the original (key, None) if there was no alias.
        """
        inst = cls.instance()
        if key in inst.column_map:
            return inst.column_map[key]
        return (key, None)
