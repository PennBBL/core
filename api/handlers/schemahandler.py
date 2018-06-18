import os
import json

from ..web import base
from .. import config


class SchemaHandler(base.RequestHandler):

    def get(self, schema):
        schema_path = os.path.join(config.schema_path, schema)
        try:
            with open(schema_path, 'rU') as f:
                return json.load(f)
        except IOError as e:
            self.abort(404, str(e))
