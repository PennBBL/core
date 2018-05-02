#!/usr/bin/env python3

import argparse
import json
import logging
import os

try:
    from pip import main as pipmain
except:
    from pip._internal import main as pipmain

SRC_DIR = os.path.abspath(os.path.dirname(__file__))
TMPL_DIR = os.path.join(SRC_DIR, 'tmpl')
GH_PAGES_DIR = os.path.abspath(os.path.join(SRC_DIR, '..', 'gh-pages'))

log = logging.getLogger('docs')

## Build documentation index to unify swagger / sdk docs
## Also (always) build index pages for branches and tags

def render_tmpl(name, dst_path, context):
    import pystache
    src_path = os.path.join(TMPL_DIR, name)
    with open(src_path, 'r') as f:
        src_tmpl = f.read()

    rendered = pystache.render(src_tmpl, context)

    with open(dst_path, 'w') as f:
        f.write(rendered)

def gen_main_page(target_dir, is_root):
    context = {}

    src_dir = os.path.join(GH_PAGES_DIR, target_dir)

    if is_root:
        context['prefix'] = target_dir + '/'
        target_dir = GH_PAGES_DIR
    else:
        target_dir = src_dir
    
    log.info('Target directory is: %s', target_dir)

    # Read version from swagger
    swagger_src = os.path.join(src_dir, 'swagger', 'swagger.json')
    try:
        with open(swagger_src, 'r') as f:
            swagger = json.load(f)
            context['version'] = swagger.get('info', {}).get('version', '')
    except IOError:
        log.exception('Could not load version from swager.json')

    index_dst = os.path.join(target_dir, 'index.md')
    log.info('Generating main template: %s', index_dst)
    render_tmpl('index.mustache', index_dst, context)

def gen_index_file(title, dest_dir):
    context = { 
        'title': title, 
        'subdirs': [] 
    }

    for name in os.listdir(dest_dir):
        if name and name[0] != '.' and os.path.isdir(os.path.join(dest_dir, name)):
            context['subdirs'].append(name + '/')

    index_dst = os.path.join(dest_dir, 'index.md')
    log.info('Generating %s index: %s', title, index_dst)
    render_tmpl('subdir_index.mustache', index_dst, context)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate documentation pages for core')
    parser.add_argument('target_dir', nargs='?', default='.', help='The target directory')
    parser.add_argument('--root', action='store_true', help='Whether or not to put the main page at gh-pages root')
    parser.add_argument('--log-level', default='info', help='log level [INFO]')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(name)s %(levelname)4.4s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=getattr(logging, args.log_level.upper()))

    # Install required packages
    log.info('Installing required packages...')
    pipmain(['install', '-qq', '-r', os.path.join(SRC_DIR, 'requirements.txt')])
    
    # Generate main template
    gen_main_page(args.target_dir, args.root)

    # Generate branches and tags index
    gen_index_file('Branches', os.path.join(GH_PAGES_DIR, 'branches'))
    gen_index_file('Tags', os.path.join(GH_PAGES_DIR, 'tags'))


