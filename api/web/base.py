import base64
import datetime
import jsonschema
import os
import pymongo
import traceback
import webapp2

from .. import util
from .. import config
from ..types import Origin
from ..auth.authproviders import AuthProvider
from ..auth.apikeys import APIKey
from ..web import errors
from elasticsearch import ElasticsearchException
from ..web.request import log_access, AccessType
from ..access_log import log_user_access


class RequestHandler(webapp2.RequestHandler):

    json_schema = None

    def __init__(self, request=None, response=None): # pylint: disable=super-init-not-called
        """Set uid, public_request, and superuser"""
        self.initialize(request, response)

        self.uid = None
        self.origin = None

        # If user is attempting to log in through `/login`, ignore Auth here:
        # In future updates, move login and logout handlers to class that overrides this init
        if self.request.path == '/api/login':
            return

        try:
            # TODO: This should be taken out of base.RequestHandler so `handle_exception()`
            # can properly catch exceptions raised by this logic as well as uninteded exceptions
            # For now, wrap in a try/catch to prevent stack traces from getting to the client
            # For more info see scitran/core #733

            self.initialization_auth()

        except Exception as e: # pylint: disable=broad-except
            error = self.handle_exception(e, self.app.debug, return_json=True)
            self.abort(error['status_code'], error['message'])


    def initialize(self, request, response):
        super(RequestHandler, self).initialize(request, response)
        request.logger.debug("Initialized request")

    def initialization_auth(self):
        drone_request = False
        session_token = self.request.headers.get('Authorization')
        drone_secret = self.request.headers.get('X-SciTran-Auth')
        drone_method = self.request.headers.get('X-SciTran-Method')
        drone_name = self.request.headers.get('X-SciTran-Name')

        self.origin = {'type': Origin.unknown, 'id': None}

        if session_token:
            if session_token.startswith('scitran-user '):
                # API key authentication
                key = session_token.split()[1]
                api_key = APIKey.validate(key)
                if api_key.get('type') == 'device':
                    self.origin = {'type': Origin.device, 'id': api_key['uid']}
                    drone_request = True  # Grant same access for backwards compatibility
                else:
                    self.uid = api_key['uid']
                    self.origin = {'type': Origin.user, 'id': self.uid}
                    if 'job' in api_key:
                        self.origin['via'] = {'type': Origin.job, 'id': api_key['job']}
            else:
                # User (oAuth) authentication
                self.uid = self.authenticate_user_token(session_token)
                self.origin = {'type': Origin.user, 'id': self.uid}

        elif drone_secret:
            if drone_method is None or drone_name is None:
                self.abort(400, 'X-SciTran-Method or X-SciTran-Name header missing')
            if config.get_item('core', 'drone_secret') is None:
                self.abort(401, 'drone secret not configured')
            if drone_secret != config.get_item('core', 'drone_secret'):
                self.abort(401, 'invalid drone secret')

            # Upsert for backwards compatibility (ie. not-yet-seen device still using drone secret)
            label = (drone_method + '_' + drone_name).replace(' ', '_')  # Note: old drone _id's are kept under label
            device = config.db.devices.find_one_and_update(
                {'label': label},
                {'$set': {'label': label, 'type': drone_method, 'name': drone_name}},
                upsert=True,
                return_document=pymongo.collection.ReturnDocument.AFTER
            )

            self.origin = {'type': Origin.device, 'id': device['_id']}
            drone_request = True

        if self.origin['type'] == Origin.device:
            # Update device.last_seen
            # In the future, consider merging any keys into self.origin?
            config.db.devices.update_one(
                {'_id': self.origin['id']},
                {'$set': {
                    'last_seen': datetime.datetime.utcnow(),
                    'errors': []  # Reset errors list if device checks in
                }})

            # Bit hackish - detect from route if a job is the origin, and if so what job ID.
            # Could be removed if routes get reorganized. POST /api/jobs/id/result, maybe?
            is_job_upload = self.request.path.startswith('/api/engine')
            job_id = self.request.GET.get('job')
            if is_job_upload and job_id is not None:
                self.origin = {'type': Origin.job, 'id': job_id}

        self.public_request = not drone_request and not self.uid

        if self.public_request:
            self.superuser_request = False
            self.user_is_admin = False
        elif drone_request:
            self.superuser_request = True
            self.user_is_admin = True
        else:
            user = config.db.users.find_one({'_id': self.uid}, ['root', 'disabled'])
            if not user:
                self.abort(402, 'User {} will need to be added to the system before managing data.'.format(self.uid))
            if user.get('disabled', False) is True:
                self.abort(402, 'User {} is disabled.'.format(self.uid))
            if user.get('root'):
                self.user_is_admin = True
            else:
                self.user_is_admin = False
            if self.is_true('root'):
                if user.get('root'):
                    self.superuser_request = True
                else:
                    self.abort(403, 'user ' + self.uid + ' is not authorized to make superuser requests')
            else:
                self.superuser_request = False

        # Format origin object to str
        if self.origin.get('type'):
            self.origin['type']         = str(self.origin['type'])
        if self.origin.get('id'):
            self.origin['id']           = str(self.origin['id'])
        if self.origin.get('via'):
            self.origin['via']['type']  = str(self.origin['via']['type'])
            self.origin['via']['id']    = str(self.origin['via']['id'])



    def authenticate_user_token(self, session_token):
        """
        AuthN for user accounts. Calls self.abort on failure.

        Returns the user's UID.
        """

        uid = None
        timestamp = datetime.datetime.utcnow()
        cached_token = config.db.authtokens.find_one({'_id': session_token})

        if cached_token:

            # Check if site has inactivity timeout
            try:
                inactivity_timeout = config.get_item('site', 'inactivity_timeout')
            except KeyError:
                inactivity_timeout = None

            if inactivity_timeout:
                last_seen = cached_token.get('last_seen')

                # If now - last_seen is greater than inactivity timeout, clear out session
                if last_seen and (timestamp - last_seen).total_seconds() > inactivity_timeout:

                    # Token expired and no refresh token, remove and deny request
                    config.db.authtokens.delete_one({'_id': cached_token['_id']})
                    config.db.refreshtokens.delete({'uid': cached_token['uid'], 'auth_type': cached_token['auth_type']})
                    self.abort(401, 'Inactivity timeout')

                # set last_seen to now
                config.db.authtokens.update_one({'_id': cached_token['_id']}, {'$set': {'last_seen': timestamp}})


            # Check if token is expired
            if cached_token.get('expires') and timestamp > cached_token['expires']:

                # look to see if the user has a stored refresh token:
                unverified_uid = cached_token['uid']
                auth_type = cached_token['auth_type']
                refresh_token = config.db.refreshtokens.find_one({'uid': unverified_uid, 'auth_type': cached_token['auth_type']})
                if refresh_token:
                    # Attempt to refresh the token, update db

                    try:
                        auth_provider = AuthProvider.factory(auth_type)
                    except NotImplementedError as e:
                        self.abort(401, str(e))

                    try:
                        updated_token_info = auth_provider.refresh_token(refresh_token['token'])
                    except errors.APIAuthProviderException as e:

                        # Remove the bad refresh token and session token:
                        config.db.refreshtokens.delete_one({'_id': refresh_token['_id']})
                        config.db.authtokens.delete_one({'_id': cached_token['_id']})

                        # TODO: Rework auth so it's not tied to init, then:
                        #   - Raise a refresh token exception specifically in this situation
                        #   - Alerts clients they may need to re-ask for `offline` permission
                        # Until then, the key `invalid_refresh_token` alerts the client
                        self.abort(401, 'invalid_refresh_token')

                    config.db.authtokens.update_one({'_id': cached_token['_id']}, {'$set': updated_token_info})

                else:
                    # Token expired and no refresh token, remove and deny request
                    config.db.authtokens.delete_one({'_id': cached_token['_id']})
                    self.abort(401, 'invalid_refresh_token')

            uid = cached_token['uid']
        else:
            self.abort(401, 'Invalid session token')

        return uid


    @log_access(AccessType.user_login)
    def log_in(self):
        """
        Return succcess boolean if user successfully authenticates.

        Used for access logging.
        Not required to use system as logged in user.
        """

        payload = self.request.json_body
        if 'code' not in payload or 'auth_type' not in payload:
            self.abort(400, 'Auth code and type required for login')

        auth_type = payload['auth_type']
        try:
            auth_provider = AuthProvider.factory(auth_type)
        except NotImplementedError as e:
            self.abort(400, str(e))

        registration_code = payload.get('registration_code')
        token_entry = auth_provider.validate_code(payload['code'], registration_code=registration_code)
        timestamp = datetime.datetime.utcnow()

        self.uid = token_entry['uid']
        self.origin = {'type': str(Origin.user), 'id': self.uid}

        # If this is the first time they've logged in, record that
        config.db.users.update_one({'_id': self.uid, 'firstlogin': None}, {'$set': {'firstlogin': timestamp}})
        # Unconditionally set their most recent login time
        config.db.users.update_one({'_id': self.uid}, {'$set': {'lastlogin': timestamp}})

        session_token = base64.urlsafe_b64encode(os.urandom(42))
        token_entry['_id'] = session_token
        token_entry['timestamp'] = timestamp

        config.db.authtokens.insert_one(token_entry)

        return {'token': session_token}


    @log_access(AccessType.user_logout)
    def log_out(self):
        """
        Remove all cached auth tokens associated with caller's uid.
        """

        token = self.request.headers.get('Authorization', None)
        if not token:
            self.abort(401, 'User not logged in.')
        result = config.db.authtokens.delete_one({'_id': token})
        return {'tokens_removed': result.deleted_count}

    def is_true(self, param):
        return self.request.GET.get(param, '').lower() in ('1', 'true')

    def get_param(self, param, default=None):
        return self.request.GET.get(param, default)

    def is_enabled(self, feature):
        """Return True if a feature is enabled (listed in the X-Accept-Feature header)"""
        return feature.lower() in self.request.headers.get('X-Accept-Feature', '').lower()

    @property
    def pagination(self):
        """
        Return parsed pagination dict from request URL parameters.

        Query params:
            ?filter=k1=v1,k2>v2,k2<v3 [, ...]
            ?sort=k1,k2:desc [, ...]
            ?page=N
            ?skip=N
            ?limit=N
        """

        pagination = {}
        parsers = {'filter': util.parse_pagination_filter_param,
                   'sort': util.parse_pagination_sort_param}

        for param_name in ('filter', 'sort', 'page', 'skip', 'limit'):
            param_count = len(self.request.GET.getall(param_name))
            if param_count > 1:
                raise errors.APIValidationException({'error': 'Multiple "{}" query params not allowed'.format(param_name)})
            if param_count > 0:
                param_value = self.request.GET.get(param_name)
                parse = parsers.get(param_name, util.parse_pagination_int_param)
                try:
                    pagination[param_name] = parse(param_value)
                except util.PaginationParseError as e:
                    raise errors.APIValidationException({'error': e.message})

        if 'page' in pagination:
            if 'skip' in pagination:
                raise errors.APIValidationException({'error': '"page" and "skip" query params are mutually exclusive'})
            if 'limit' not in pagination:
                raise errors.APIValidationException({'error': '"limit" query param is required with "page"'})
            pagination['skip'] = pagination['limit'] * (pagination.pop('page') - 1)

        return pagination

    def format_page(self, page):
        """
        Return page (dict with total and results) if `pagination` feature is enabled.
        Return `page['results']` (list) otherwise, for backwards compatibility.
        """
        if not self.is_enabled('pagination'):
            return page['results']
        page['count'] = len(page['results'])
        return page

    def handle_exception(self, exception, debug, return_json=False): # pylint: disable=arguments-differ
        """
        Send JSON response for exception

        For HTTP and other known exceptions, use its error code
        For all others use a generic 500 error code and log the stack trace
        """

        request_id = self.request.id
        custom_errors = None
        message = str(exception)
        if isinstance(exception, webapp2.HTTPException):
            code = exception.code
        elif isinstance(exception, errors.InputValidationException):
            code = 400
        elif isinstance(exception, errors.APIAuthProviderException):
            code = 401
        elif isinstance(exception, errors.APIRefreshTokenException):
            code = 401
            custom_errors = exception.errors
        elif isinstance(exception, errors.APIUnknownUserException):
            code = 402
        elif isinstance(exception, errors.APIConsistencyException):
            code = 400
        elif isinstance(exception, errors.APIPermissionException):
            custom_errors = exception.errors
            code = 403
        elif isinstance(exception, errors.APINotFoundException):
            code = 404
        elif isinstance(exception, errors.APIConflictException):
            code = 409
        elif isinstance(exception, errors.APIValidationException):
            code = 422
            custom_errors = exception.errors
        elif isinstance(exception, errors.FileStoreException):
            code = 400
        elif isinstance(exception, errors.FileFormException):
            code = 400
        elif isinstance(exception, errors.FileFormException):
            code = 400
        elif isinstance(exception, ElasticsearchException):
            code = 503
            message = "Search is currently down. Try again later."
            self.request.logger.error(traceback.format_exc())
        elif isinstance(exception, KeyError):
            code = 500
            message = "Key {} was not found".format(str(exception))
        else:
            code = 500

        if code == 500:
            tb = traceback.format_exc()
            self.request.logger.error(tb)

        if return_json:
            return util.create_json_http_exception_response(message, code, request_id, custom=custom_errors)

        util.send_json_http_exception(self.response, message, code, request_id, custom=custom_errors)

    def log_user_access(self, access_type, cont_name=None, cont_id=None, filename=None, multifile=False, origin_override=None):
        origin = origin_override if origin_override is not None else self.origin
        ticket = self.get_param('ticket')

        try:
            log_user_access(self.request, access_type, cont_name=cont_name, cont_id=cont_id,
                    filename=filename, multifile=multifile, origin=origin, download_ticket=ticket)
        except Exception as e:  # pylint: disable=broad-except
            config.log.exception(e)
            self.abort(500, 'Unable to log access.')

    def dispatch(self):
        """dispatching and request forwarding"""

        self.request.logger.debug('from %s %s %s %s', self.uid, self.request.method, self.request.path, str(self.request.GET.mixed()))
        return super(RequestHandler, self).dispatch()

    # pylint: disable=arguments-differ
    def abort(self, code, detail=None, **kwargs):
        if isinstance(detail, jsonschema.ValidationError):
            detail = {
                'relative_path': list(detail.relative_path),
                'instance': detail.instance,
                'validator': detail.validator,
                'validator_value': detail.validator_value,
            }
        self.request.logger.warning(str(self.uid) + ' ' + str(code) + ' ' + str(detail))
        webapp2.abort(code, detail=detail, **kwargs)
