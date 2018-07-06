import os, random, string, json, shutil, tempfile
from datetime import datetime, timedelta
import dateutil.tz
import flywheel
import unittest
from six.moves.urllib.parse import urlparse
import init_db

HEX_DIGITS = '0123456789abcdef'
TD_ZERO = timedelta()
TZ_UTC = dateutil.tz.tzutc()

def utcnow():
    # datetime requires tzinfo for comparison
    return datetime.utcnow().replace(tzinfo=TZ_UTC)

def make_clients():
    api_key = None
    if init_db.SCITRAN_PERSISTENT_DB_URI:
        # Initialize database first
        init_db.init_db()

        site_url = urlparse(os.environ['SCITRAN_SITE_API_URL'])
        api_key = '{}:__force_insecure:{}'.format(site_url.netloc, init_db.SCITRAN_ADMIN_API_KEY)
    else:
        api_key = os.environ.get('SdkTestKey')

    if not api_key:
        print('Could not initialize test case, no api_key. Try setting the SdkTestKey environment variable!')
        exit(1)

    fw = flywheel.Flywheel(api_key)
    fw.enable_feature('beta')

    # Mock cli login
    home = os.environ['HOME']
    os.environ['HOME'] = tmp_path = tempfile.mkdtemp()
    cli_config_path = os.path.expanduser('~/.config/flywheel/')
    if not os.path.exists(cli_config_path):
        os.makedirs(cli_config_path)
    with open(os.path.join(cli_config_path, 'user.json'), 'w') as cli_config:
        json.dump({'key': api_key}, cli_config)

    client = flywheel.Client()
    client.enable_feature('beta')

    # Don't need the login anymore
    shutil.rmtree(tmp_path)
    os.environ['HOME'] = home

    return fw, client

class SdkTestCase(unittest.TestCase):
    fw, client = make_clients()

    @classmethod
    def rand_string_lower(self, length=10):
        return self._rand_string(length, string.ascii_lowercase)

    @classmethod
    def rand_string(self, length=10):
        return self._rand_string(length, string.ascii_lowercase + string.ascii_uppercase)

    @classmethod
    def rand_hex(self, length=24):
        return self._rand_string(length, HEX_DIGITS)

    @classmethod
    def _rand_string(self, length, glyphs):
        return ''.join( random.choice(glyphs) for _ in range(length) )

    def assertNotEmpty(self, container):
        if container is None or len(container) == 0:
            raise AssertionError('Expected a non-empty value, got: "' + str(container) + '" instead.')

    def assertEmpty(self, container):
        if container is not None and len(container) > 0:
            raise AssertionError('Expected an empty value, got: "' + str(container) + '" instead.')

    def assertTimestampNear(self, value, expected, toleranceSec=5):
        d_allowed = timedelta(seconds=toleranceSec)
        d_actual = abs(expected - value)
        if d_actual > d_allowed:
            raise AssertionError('Expected time ' + str(value) + ' to be close to ' + str(expected))

    def assertTimestampNearNow(self, value, toleranceSec=5):
        self.assertTimestampNear(value, utcnow(), toleranceSec)

    def assertTimestampBefore(self, value, expected, toleranceSec=0):
        if toleranceSec:
            expected = expected + timedelta(seconds=toleranceSec)
        if (expected - value) < TD_ZERO:
            raise AssertionError('Expected time ' + str(value) + ' to be before ' + str(expected))

    def assertTimestampBeforeNow(self, value, toleranceSec=5):
        self.assertTimestampBefore(value, utcnow(), toleranceSec)

    def assertTimestampAfter(self, value, expected, toleranceSec=0):
        if toleranceSec:
            expected = expected - timedelta(seconds=toleranceSec)
        if (expected - value) > TD_ZERO:
            raise AssertionError('Expected time ' + str(value) + ' to be after ' + str(expected))

    def assertDownloadFileTextEquals(self, method, id, filename, expected):
        content = method(id, filename)
        self.assertIsNotNone(content)
        content = content.decode('utf-8')

        self.assertEqual(content, expected)

    def assertDownloadFileTextEqualsWithTicket(self, method, id, filename, expected):
        download_url = method(id, filename)

        self.assertIsNotNone(download_url)

        resp = self.fw.api_client.rest_client.GET(download_url, _preload_content=False)
        self.assertIsNotNone(resp)
        try:
            self.assertEqual(resp.status_code, 200)

            content = resp.content
            self.assertIsNotNone(content)

            content = content.decode('utf-8')

            self.assertEqual(content, expected)
        finally:
            resp.close()
