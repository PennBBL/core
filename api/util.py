import datetime
import enum as baseEnum
import hashlib
import json
import mimetypes
import os
import random
import re
import requests
import string
import uuid

import bson
import django
from django.conf import settings
from django.template import Template, Context
import fs.path
import fs.errors
import pymongo

from .web.errors import InputValidationException


BYTE_RANGE_RE = re.compile(r'^(?P<first>\d+)-(?P<last>\d+)?$')
SUFFIX_BYTE_RANGE_RE = re.compile(r'^(?P<first>-\d+)$')
DATETIME_RE = {
    re.compile(r'^\d\d\d\d-\d\d-\d\d$'):                              '%Y-%m-%d',
    re.compile(r'^\d\d\d\d-\d\d-\d\dT\d\d:\d\d$'):                    '%Y-%m-%dT%H:%M',
    re.compile(r'^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d$'):               '%Y-%m-%dT%H:%M:%S',
    re.compile(r'^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d\d\d\d$'): '%Y-%m-%dT%H:%M:%S.%f',
}


# If this is not called before templating, django throws a hissy fit
settings.configure(
    TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates'}],
)
django.setup()

def render_template(template, context):
    """
    Dead-simple wrapper to call django text templating.
    Set up your own Template and Context objects if re-using heavily.
    """

    t = Template(template)
    c = Context(context)
    return t.render(c)


MIMETYPES = [
    ('.bvec', 'text', 'bvec'),
    ('.bval', 'text', 'bval'),
    ('.m', 'text', 'matlab'),
    ('.sh', 'text', 'shell'),
    ('.r', 'text', 'r'),
]
for mt in MIMETYPES:
    mimetypes.types_map.update({mt[0]: mt[1] + '/' + mt[2]})

# NOTE unused function
def hrsize(size):
    if size < 1000:
        return '%d%s' % (size, 'B')
    for suffix in 'KMGTPEZY':
        size /= 1024.
        if size < 10.:
            return '%.1f%sB' % (size, suffix)
        if size < 1000.:
            return '%.0f%sB' % (size, suffix)
    return '%.0f%sB' % (size, 'Y')

def mongo_sanitize(field):
    return field.replace('.', '_')

def mongo_dict(d, prefix=''):
    """
    Return a flattened dictionary of sanitized keys for a mongo update.
    """
    def _mongo_list(d, pk=''):
        pk = pk and pk + '.'
        return sum(
            [
            _mongo_list(v, pk+mongo_sanitize(k)) if isinstance(v, dict) else [(pk+mongo_sanitize(k), v)]
            for k, v in d.iteritems()
            ], []
        )
    return dict(_mongo_list(d, pk=prefix))

def mongo_sanitize_fields(d):
    """
    Sanitize keys of arbitrarily structured map without flattening into dot notation

    Adapted from http://stackoverflow.com/questions/8429318/how-to-use-dot-in-field-name
    """

    if isinstance(d, dict):
        return {mongo_sanitize_fields(str(key)): value if isinstance(value, str) else mongo_sanitize_fields(value) for key,value in d.iteritems()}
    elif isinstance(d, list):
        return [mongo_sanitize_fields(element) for element in d]
    elif isinstance(d, str):
        # not allowing dots nor dollar signs in fieldnames
        d = d.replace('.', '_')
        d = d.replace('$', '-')
        if d is '':
            raise InputValidationException("'' not allowed as Mongo key name")
        return d
    else:
        return d

def deep_update(d, u):
    """
    Makes a deep update of dict d with dict u
    Adapted from http://stackoverflow.com/a/3233356
    """
    for k, v in u.iteritems():
        if isinstance(v, dict):
            r = deep_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def user_perm(permissions, _id):
    for perm in permissions:
        if str(perm['_id']) == str(_id):
            return perm
    return {}


def is_user_id(uid):
    """
    Checks to make sure uid matches uid regex
    """
    pattern = re.compile('^[0-9a-f]{24}$')
    return bool(pattern.match(str(uid)))


# NOTE unused function
def is_group_id(gid):
    """
    Checks to make sure uid matches uid regex
    """
    pattern = re.compile('^[0-9a-z][0-9a-z.@_-]{0,30}[0-9a-z]$')
    return bool(pattern.match(gid))


def datetime_from_str(s):
    """
    Return datetime.datetime parsed from a string that is a prefix of isoformat.
    Return None if the string is not such a valid prefix.
    """
    for date_re, date_fmt in DATETIME_RE.iteritems():
        if date_re.match(s):
            return datetime.datetime.strptime(s, date_fmt)
    return None


def resolve_gravatar(email):
    """
    Given an email, returns a URL if that email has a gravatar set.
    Otherwise returns None.
    """

    gravatar = 'https://gravatar.com/avatar/' + hashlib.md5(email).hexdigest() + '?s=512'
    if requests.head(gravatar, params={'d': '404'}):
        return gravatar
    else:
        return None


# NOTE unused function
def container_fileinfo(container, filename): # pragma: no cover
    for fileinfo in container.get('files', []):
        if fileinfo['filename'] == filename:
            return fileinfo
    return None


def download_ticket(ip, origin, type_, target, filename, size, projects = None):
    return {
        '_id': str(uuid.uuid4()),
        'timestamp': datetime.datetime.utcnow(),
        'ip': ip,
        'type': type_,
        'target': target,
        'filename': filename,
        'size': size,
        'projects': projects or [],
        'origin': origin
    }


def upload_ticket(ip, origin, tempdir, filenames, metadata):
    return {
        '_id': str(uuid.uuid4()),
        'timestamp': datetime.datetime.utcnow(),
        'ip': ip,
        'tempdir': tempdir,
        'filenames': filenames,
        'metadata': metadata,
        'origin': origin
    }


def guess_mimetype(filepath):
    """Guess MIME type based on filename."""
    mime, _ = mimetypes.guess_type(filepath)
    return mime or 'application/octet-stream'

def sanitize_string_to_filename(value):
    """
    Best-effort attempt to remove blatantly poor characters from a string before turning into a filename.

    Happily stolen from the internet, then modified.
    http://stackoverflow.com/a/7406369
    """

    keepcharacters = (' ', '.', '_', '-')
    return "".join([c for c in value if c.isalnum() or c in keepcharacters]).rstrip()

def sanitize_path(filepath):
    """
    Ensures that a path does not attempt to leave a directory,
    i.e. ../place/I/should/not/be is not allowed so it gets converted to
    place/I/should/not/be
    """
    return os.path.normpath('/'+filepath).lstrip('/')

def obj_from_map(_map):
    """
    Creates an anonymous object with properties determined by the passed (shallow) map.
    Hides the esoteric python syntax.
    """

    return type('',(object,),_map)()

def set_for_download(response, stream=None, filename=None, length=None):
    """Takes a self.response, and various download options."""

    # If an app_iter is to be set, it MUST be before these other headers are set.
    if stream is not None:
        response.app_iter = stream

    response.headers['Content-Type'] = 'application/octet-stream'

    if filename is not None:
        response.headers['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    if length is not None:
        response.headers['Content-Length'] = str(length)

def format_hash(hash_alg, hash_):
    """
    format the hash including version and algorithm
    """
    return '-'.join(('v0', hash_alg, hash_))

def create_json_http_exception_response(message, code, request_id, core_status_code=None, custom=None):
    content = {
        'message': message,
        'status_code': code,
        'request_id': request_id
    }
    if core_status_code:
        content['core_status_code'] = core_status_code
    if custom:
        content.update(custom)
    return content

def send_json_http_exception(response, message, code, request_id, core_status_code=None, custom=None):
    response.set_status(code)
    json_content = json.dumps(create_json_http_exception_response(message, code, request_id, core_status_code, custom))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.write(json_content)

class Enum(baseEnum.Enum):
    # Enum strings are prefixed by their class: "Category.classifier".
    # This overrides that behaviour and removes the prefix.
    def __str__(self):
        return str(self.name)

    # Allow equality comparison with strings against the enum's name.

    def __ne__(self, other):
        if isinstance(other, basestring):
            return self.name != other
        else:
            return super.__ne__(other)

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.name == other
        else:
            return super.__eq__(other)

def mkdir_p(path, file_system):
    try:
        file_system.makedirs(path)
    except fs.errors.DirectoryExists:
        pass

NONCE_CHARS  = string.ascii_letters + string.digits
NONCE_LENGTH = 18

def create_nonce():
    x = len(NONCE_CHARS)

    # Class that uses the os.urandom() function for generating random numbers.
    # https://docs.python.org/2/library/random.html#random.SystemRandom
    randrange = random.SystemRandom().randrange

    return ''.join([NONCE_CHARS[randrange(x)] for _ in range(NONCE_LENGTH)])


def path_from_uuid(uuid_):
    """
    create a filepath from a UUID
    e.g.
    uuid_ = cbb33a87-6754-4dfd-abd3-7466d4463ebc
    will return
    cb/b3/cbb33a87-6754-4dfd-abd3-7466d4463ebc
    """
    uuid_1 = uuid_.split('-')[0]
    first_stanza = uuid_1[0:2]
    second_stanza = uuid_1[2:4]
    path = (first_stanza, second_stanza, uuid_)
    return fs.path.join(*path)


def path_from_hash(hash_):
    """
    create a filepath from a hash
    e.g.
    hash_ = v0-sha384-01b395a1cbc0f218
    will return
    v0/sha384/01/b3/v0-sha384-01b395a1cbc0f218
    """
    hash_version, hash_alg, actual_hash = hash_.split('-')
    first_stanza = actual_hash[0:2]
    second_stanza = actual_hash[2:4]
    path = (hash_version, hash_alg, first_stanza, second_stanza, hash_)
    return os.path.join(*path)


class RangeHeaderParseError(ValueError):
    """Exception class representing a string parsing error."""


def build_content_range_header(first, last, size):
    if last == None:
        last = size-1

    return 'bytes %s-%s/%s' % (str(first), str(last), str(size))


def parse_range_header(range_header_val, valid_units=('bytes',)):
    """
    Range header parser according to RFC7233

    https://tools.ietf.org/html/rfc7233
    """

    split_range_header_val = range_header_val.split('=')
    if not len(split_range_header_val) == 2:
        raise RangeHeaderParseError('Invalid range header syntax')

    unit, ranges_str = split_range_header_val

    if unit not in valid_units:
        raise RangeHeaderParseError('Invalid unit specified')

    split_ranges_str = ranges_str.split(', ')

    ranges = []

    for range_str in split_ranges_str:
        re_match = BYTE_RANGE_RE.match(range_str)
        first, last = None, None

        if re_match:
            first, last = re_match.groups()
        else:
            re_match = SUFFIX_BYTE_RANGE_RE.match(range_str)
            if re_match:
                first = re_match.group('first')
            else:
                raise RangeHeaderParseError('Invalid range format')

        if first is not None:
            first = int(first)


        if last is not None:
            last = int(last)

        if last is not None and first > last:
            raise RangeHeaderParseError('Invalid range, first %s can\'t be greater than the last %s' % (unit, unit))

        ranges.append((first, last))

    return ranges


class PaginationParseError(ValueError):
    """Exception class for invalid pagination params."""
    pass


def parse_pagination_value(value):
    """Return casted value (ObjectId|datetime|float) from user input (str) for use in mongo queries."""
    if len(value) > 1 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    elif bson.ObjectId.is_valid(value):
        return bson.ObjectId(value)
    elif datetime_from_str(value):
        return datetime_from_str(value)
    elif value == 'null':
        return None
    else:
        try:
            # Note: querying for floats also yields ints (=> no need for int casting here)
            return float(value)
        except ValueError:
            pass
    return value


def parse_pagination_filter_param(filter_param):
    """Return parsed pagination filter (dict) from filter param (str)."""
    pagination_filter = {}
    filter_ops = {'<':  '$lt',
                  '<=': '$lte',
                  '=':  '$eq',
                  '!=': '$ne',
                  '>=': '$gte',
                  '>':  '$gt',
                  '=~': '$regex'}
    for filter_str in filter_param.split(','):
        for filter_op in sorted(filter_ops, key=len, reverse=True):
            key, op, value = filter_str.partition(filter_op)
            if op:
                if key not in pagination_filter:
                    pagination_filter[key] = {}
                pagination_filter[key].update({filter_ops[op]: parse_pagination_value(value)})
                break
        else:
            raise PaginationParseError('Invalid pagination filter: {} (operator missing)'.format(filter_str))

    return pagination_filter


def parse_pagination_sort_param(sort_param):
    """Return parsed pagination sorting (list of (key, order) tuples) from sort param (str)."""
    pagination_sort  = []
    sort_orders = { '1': pymongo.ASCENDING,   'asc': pymongo.ASCENDING,
                   '-1': pymongo.DESCENDING, 'desc': pymongo.DESCENDING}
    for sort_str in sort_param.split(','):
        key, _, order = sort_str.partition(':')
        order = order.lower() or 'asc'
        if order not in sort_orders:
            raise PaginationParseError('Invalid pagination sort: {} (unknown order)'.format(sort_str))
        pagination_sort.append((key, sort_orders[order]))

    return pagination_sort


def parse_pagination_int_param(int_param):
    """Return positive int parsed from string."""
    try:
        pagination_int = int(int_param)
        if pagination_int <= 0:
            raise ValueError('expected positive integer, got {}'.format(pagination_int))
    except ValueError as e:
        raise PaginationParseError('Invalid pagination int: {}'.format(e.message))

    return pagination_int


class dotdict(dict):
    def __getattr__(self, name):
        return self[name]

def origin_to_str(origin):
    """Format an origin dictionary as a string"""
    result = str(origin['type'])
    origin_id = origin.get('id')
    if origin_id:
        result += ':%s' % origin_id
    if 'via' in origin:
        result += ' (via %s)' % origin_to_str(origin['via'])
    return result

def add_container_type(request, result):
    """Adds a 'container_type' property to result if fw_container_type is set in the request environment."""
    if 'fw_container_type' in request.environ and isinstance(result, dict):
        result['container_type'] = request.environ['fw_container_type']
