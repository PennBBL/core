import datetime as dt

from ..web import base
from .. import config
from .. import util
from ..auth import require_drone, require_login, require_admin
from ..auth.apikeys import DeviceApiKey
from ..dao import containerstorage
from ..web.errors import APINotFoundException, APIValidationException, APIException
from ..validators import validate_data

log = config.log

Status = util.Enum('Status', {
    'ok':       'ok',       # Device's last seen time is shorter than expected interval for checkin, no errors listed.
    'missing':  'missing',  # Device's last seen time is longer than the expected interval for checkin, but no errors listed.
    'error':    'error' ,   # Device has errors listed.
    'unknown':  'unknown'   # Device did not set an expected checkin interval.
})


def get_device_statuses(devices):
    now = dt.datetime.now()
    statuses = {}
    for device in devices:
        status = {'last_seen': device.get('last_seen')}
        if device.get('errors'):
            status['status'] = str(Status.error)
            status['errors'] = device['errors']
        elif not device.get('interval') or not device.get('last_seen'):
            status['status'] = str(Status.unknown)
        elif (now - device['last_seen']).seconds > device['interval']:
            status['status'] = str(Status.missing)
        else:
            status['status'] = str(Status.ok)
        statuses[str(device['_id'])] = status

    return statuses

class DeviceHandler(base.RequestHandler):

    def __init__(self, request=None, response=None):
        super(DeviceHandler, self).__init__(request, response)
        self.storage = containerstorage.ContainerStorage('devices', use_object_id=True)

    @require_login
    def get(self, device_id):
        device = self.storage.get_container(device_id)
        if self.user_is_admin:
            self.join_api_key(device)
        return device

    @require_login
    def get_all(self):
        page = self.storage.get_all_el(None, None, None, pagination=self.pagination)
        devices = page['results']
        if self.user_is_admin and self.is_true('join_keys'):
            for device in devices:
                self.join_api_key(device)
        return self.format_page(page)

    @staticmethod
    def join_api_key(device):
        api_key = DeviceApiKey.get(device['_id'])
        device['key'] = api_key['_id'] if api_key else DeviceApiKey.generate(device['_id'])

    @require_admin
    def post(self):
        payload = self.request.json_body if self.request.body else {}

        # Temp device check-in backwards-compatibility
        if self.origin.get('type') == 'device':
            return self.put_self()

        validate_data(payload, 'device.json', 'input', 'POST', optional=True)
        result = self.storage.create_el(payload)
        if not result.acknowledged:
            raise APINotFoundException('Device not created')
        key = DeviceApiKey.generate(result.inserted_id)
        return {'_id': result.inserted_id, 'key': key}

    @require_admin
    def delete(self, device_id):
        result = self.storage.delete_el(device_id)
        if result.deleted_count != 1:
            raise APINotFoundException('Device not found')
        return {'deleted': result.deleted_count}

    @require_login
    def get_status(self):
        return get_device_statuses(self.storage.get_all_el(None, None, None))

    @require_drone
    def put_self(self):
        device_id = self.origin.get('id', '')
        device = self.storage.get_container(device_id)

        if not self.request.body:
            return {'modified': 0}

        payload = self.request.json_body
        validate_data(payload, 'device-update.json', 'input', 'PUT', optional=True)

        # New devices created via POST may have `type` not set. Devices are allowed to initialize
        # the field themselves, but not allowed to change it (which implies a different device).
        if 'type' in payload and device.get('type') not in (None, payload['type']):
            raise APIValidationException(reason='Cannot change device type')

        result = self.storage.update_el(device_id, payload)
        return {'modified': result.modified_count}

    @require_drone
    def serve_logging_credentials(self, filename):
        if filename in ['client_cert.pem', 'client_key.pem', 'ca.pem']:
            self.response.headers['Content-Type'] = 'application/x-x509-ca-cert'
            try:
                with open('/var/scitran/keys/log_clients/{}'.format(filename)) as data:
                    self.response.write(data.read())
            except IOError:
                raise APIException('File {} not found! Make sure centralized logging is set up'.format(filename))
        elif filename in ['remote_config', 'local_config']:
            self.response.headers['Content-Type'] = 'text/plain'
            try:
                with open('/var/scitran/keys/log_clients/{}'.format(filename)) as data:
                    self.response.write(data.read())
            except IOError:
                raise APIException('File {} not found! Make sure centralized logging is set up'.format(filename))
        else:
            raise APINotFoundException('File {} is not a valid logging credential'.format(filename))
