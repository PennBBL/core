'''
The purpose of this file is to override the _static hosting path for
theme files, to reduce the overall size of the gh-pages branch.

This is done by wrapping the TemplateBridge, and overriding the pathto
jinja function to replace the _static prefix with the configured value.

Set statichtml_path config option to a global theme folder (e.g. /themes/sphinx_rtd/0.2.4)
'''
import os
import shutil

from sphinx.application import TemplateBridge
from sphinx.builders.html import StandaloneHTMLBuilder

def static_wrap_pathto(context, static_prefix=None, static_path=None):
    if 'pathto' in context:
        orig = context['pathto']

        def pathto(*args):
            if static_path:
                otheruri = args[0]
                if otheruri and otheruri.startswith('_static'):
                    if static_prefix:
                        return static_prefix + static_path + otheruri[7:]
                    else:
                        return static_path + otheruri[7:]

            return orig(*args) 
        
        context['pathto'] = pathto

class TemplateBridgeWrapper(TemplateBridge):
    def __init__(self, wrapped, static_prefix, static_path):
        self.wrapped = wrapped
        self.static_prefix = static_prefix
        self.static_path = static_path

    def newest_template_mtime(self):
        return self.wrapped.newest_template_mtime()

    def render(self, template, context):
        static_wrap_pathto(context, self.static_prefix, self.static_path)
        return self.wrapped.render(template, context)

    def render_string(self, source, context):
        static_wrap_pathto(context, self.static_prefix, self.static_path)
        return self.wrapped.render_string(source, context)

class StaticHTMLBuilder(StandaloneHTMLBuilder):
    name = 'statichtml'

    def init_templates(self):
        super(StaticHTMLBuilder, self).init_templates()

        # Wrap templates, and override pathto
        self.templates = TemplateBridgeWrapper(self.templates, 
            self.config.statichtml_prefix, self.config.statichtml_path)

    def handle_finish(self):
        super(StaticHTMLBuilder, self).handle_finish()

        # Move static files
        dst_path = self.config.statichtml_path
        if dst_path:
            static_dir = os.path.join(self.outdir, '_static')
            dst_dir = os.path.join(self.outdir, dst_path) 

            if os.path.isdir(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.move(static_dir, dst_dir)

def setup(app):
    app.add_config_value('statichtml_prefix', None, 'html')
    app.add_config_value('statichtml_path', None, 'html')
    app.add_builder(StaticHTMLBuilder)

