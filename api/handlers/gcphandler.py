import itertools
import json
import os
import re
from collections import OrderedDict

import bson
import datetime
import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

from .. import config
from ..auth import require_login
from ..dao import containerutil
from ..dao.hierarchy import get_parent_tree
from ..data_views.storage import DataViewStorage
from ..jobs.gears import get_latest_gear
from ..jobs.queue import Queue
from ..web import base
from ..web.errors import APIException, APINotFoundException, APIValidationException

# get default config from env
GHC_KEY_JSON = os.environ.get('GHC_KEY_JSON')
GHC_PROJECT = os.environ.get('GHC_PROJECT')
if GHC_KEY_JSON and not GHC_PROJECT:
    GHC_PROJECT = json.load(open(GHC_KEY_JSON))['project_id']
GHC_LOCATION = os.environ.get('GHC_LOCATION', 'us-central1')
GHC_DATASET = os.environ.get('GHC_DATASET', 'ghc')
GHC_DICOMSTORE = os.environ.get('GHC_DICOMSTORE', 'ghc')

SQL_LIMIT = 100
SQL_TEMPLATE = """
SELECT
  StudyInstanceUID, SeriesInstanceUID,
  MIN(AccessionNumber) AS AccessionNumber,
  MIN(PatientID) AS PatientID,
  MIN(StudyID) AS StudyID,
  MIN(StudyDate) AS StudyDate,
  MIN(StudyTime) AS StudyTime,
  MIN(StudyDescription) AS StudyDescription,
  MIN(SeriesDate) AS SeriesDate,
  MIN(SeriesTime) AS SeriesTime,
  MIN(SeriesDescription) AS SeriesDescription,
  COUNT(DISTINCT SOPInstanceUID) AS instance_count
FROM {dataset}.{table}
WHERE {where}
GROUP BY StudyInstanceUID, SeriesInstanceUID
ORDER BY StudyInstanceUID, SeriesInstanceUID
LIMIT {limit}
OFFSET {offset}
"""
SQL_DETAIL_TEMPLATE = """
SELECT *
FROM {dataset}.{table}
WHERE StudyInstanceUID="{uid}" OR SeriesInstanceUID="{uid}"
ORDER BY StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID
LIMIT 1
"""

SEARCH_CONTAINERS = ['projects', 'subjects', 'sessions', 'acquisitions']


class GCPHandler(base.RequestHandler):
    @require_login
    def generate_token(self):
        """Generate temp GHC access token using FW Core's service account if available"""
        token = generate_service_account_token()
        if not token:
            self.abort(500, 'service account not configured')
        return {'token': token}


class GHCHandler(base.RequestHandler):
    @require_login
    def run_query(self):
        """Run BigQuery and return formatted results (studies and sessions in hierarchy)"""
        payload = self.request.json_body
        params = {
            'dataset': payload.get('dataset', GHC_DATASET),
            'table': payload.get('table', GHC_DICOMSTORE),
            'where': payload.get('where', '1=1'),
            'limit': min(payload.get('limit', SQL_LIMIT), SQL_LIMIT),
            'offset': payload.get('offset', 0),
        }
        result = self.bigquery.run_query(SQL_TEMPLATE.format(**params))
        return format_query_result(result)

    @require_login
    def run_details_query(self):
        """Run BigQuery and return all cols of the 1st instance matching study/session uid"""
        payload = self.request.json_body
        if 'uid' not in payload:
            self.abort(400, 'uid not in payload')
        params = {
            'dataset': payload.get('dataset', GHC_DATASET),
            'table': payload.get('table', GHC_DICOMSTORE),
            'uid': payload['uid'],
        }
        result = self.bigquery.run_query(SQL_DETAIL_TEMPLATE.format(**params))
        record = next(result['rows'], None)
        if not record:
            self.abort(404, 'cannot find study/series {}'.format(payload['uid']))
        return OrderedDict([(key, value) for key, value in sorted(record.iteritems(), key=lambda i: i[0]) if value])

    @require_login
    def run_import(self):
        """Run ghc-importer gear"""
        payload = self.request.json_body
        query_id = payload.get('query_id')
        uid_field = 'StudyInstanceUID' if payload.get('study') else 'SeriesInstanceUID'
        uids = payload.get('uids', [])
        exclude_uids = payload.get('exclude', [])

        if query_id:
            result = self.bigquery.get_query(query_id)
            uids = set(row[uid_field] for row in result['rows'])
            uids.difference_update(exclude_uids)
        elif uids:
            uids = set(uids)
        if not uids:
            self.abort(400, 'nothing to import')

        gear = get_latest_gear('ghc-import')
        if not gear:
            self.abort(404, 'ghc-import gear is not installed')

        group_id = payload['group_id']
        project_label = payload['project_label']
        project = config.db.projects.find_one({'group': group_id, 'label': project_label})
        if not project:
            self.abort(404, 'project "{}" does not exist'.format(project_label))

        job_payload = {
            'gear_id': gear['_id'],
            'destination': {'type': 'project', 'id': project['_id']},
            'config': {
                'hc_project': payload.get('project', GHC_PROJECT),
                'hc_location': payload.get('location', GHC_LOCATION),
                'hc_dataset': payload.get('dataset', GHC_DATASET),
                'hc_datastore': payload.get('dicomstore', GHC_DICOMSTORE),
                'uids': list(uids),
                'uid_field': uid_field,
                'de_identify': payload.get('de_identify', False),
                'group_id': payload['group_id'],
                'project_label': payload['project_label'],
            }
        }

        # TODO security - hide / get from user profile / TBD
        if payload.get('token'):
            job_payload['config']['token'] = payload['token']

        job = Queue.enqueue_job(job_payload, self.origin)
        job.insert()
        return {'_id': job.id_}

    @property
    def bigquery(self):
        payload = self.request.json_body
        project = payload.get('project', GHC_PROJECT)
        if not project:
            self.abort(400, 'project not in payload (default not configured)')
        elif 'token' not in payload and project != GHC_PROJECT:
            self.abort(400, 'token not in payload (required with custom project)')
        token = payload.get('token') or generate_service_account_token()
        if not token:
            self.abort(400, 'token not in payload (service account not configured)')
        return BigQuery(project, token)

    @require_login
    def get_jobs(self):
        import_jobs = config.db.jobs.find({'gear_info.name': 'ghc-import'}, sort=[('created', -1)])
        result = {
            'success': 0,
            'pending': 0,
            'failed': 0,
            'running': 0,
            'jobs': []
        }

        for job in import_jobs:
            if job['state'] == 'complete':
                result['success'] += 1
            if job['state'] == 'pending':
                result['pending'] += 1
            if job['state'] == 'failed':
                result['failed'] += 1
            if job['state'] == 'running':
                result['running'] += 1

            result['jobs'].append(job)

        return result

    @require_login
    def run_statistics(self):
        payload = self.request.json_body
        statistic_query = """
        SELECT
          COUNT(DISTINCT StudyInstanceUID) AS studies_count,
          COUNT(DISTINCT SeriesInstanceUID) AS series_count,
          COUNT(DISTINCT SOPInstanceUID) AS instance_count
        FROM {dataset}.{table}
        WHERE {where}
        """
        params = {
            'dataset': payload.get('dataset', GHC_DATASET),
            'table': payload.get('table', GHC_DICOMSTORE),
            'where': payload.get('where', '1=1')
        }
        result = self.bigquery.run_query(statistic_query.format(**params))
        record = next(result['rows'], None)
        if not record:
            self.abort(404, 'cannot find any recors in {}/{}'.format(params['dataset'], params['table']))
        return {key: value for key, value in record.iteritems() if value}

    @require_login
    def get_schema(self):
        payload = self.request.json_body
        params = {
            'dataset': payload.get('dataset', GHC_DATASET),
            'table': payload.get('table', GHC_DICOMSTORE)
        }
        return self.bigquery.get_table(**params)


class BigQueryHandler(base.RequestHandler):

    @require_login
    def export_view(self):
        """Run data view pipeline and export it to BigQuery"""
        gear = get_latest_gear('view-bq-export')
        if not gear:
            self.abort(404, 'view-bq-export gear is not installed')

        payload = self.request.json_body

        container_id = payload['container_id']

        if bson.ObjectId.is_valid(container_id):
            container_id = bson.ObjectId(container_id)

        result = containerutil.container_search({'_id': container_id}, collections=SEARCH_CONTAINERS)
        if not result:
            raise APINotFoundException('Could not resolve container: {}'.format(payload['container_id']))
        cont_type, search_results = result[0]

        table_id_parts = []

        view_spec = None

        if payload.get('view_id'):
            storage = DataViewStorage()
            cont = storage.get_el(payload['view_id'])
            parent_container = storage.get_parent(payload['view_id'], cont=cont)
            if parent_container.get('label'):
                table_id_parts.append(re.sub('[^A-Za-z0-9]+', '', parent_container['label']))
            else:
                table_id_parts.append(parent_container['_id'])
            table_id_parts.append(re.sub('[^A-Za-z0-9]+', '', cont['label']))
        elif payload.get('json'):
            view_spec = payload['json']

            hierarchy = get_parent_tree(cont_type, payload['container_id'])
            for _cont_name in ['group', 'project', 'subject', 'session', 'acquisition']:
                if hierarchy.get(_cont_name):
                    table_id_parts.append(re.sub('[^A-Za-z0-9]+', '', hierarchy.get(_cont_name).get('label', '')))

            table_id_parts.append(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        else:
            raise APIValidationException('Invalid request, one of json and view_id fields is required')

        job_payload = {
            'gear_id': gear['_id'],
            'destination': {'type': cont_type, 'id': search_results[0]['_id']},
            'config': {
                'container_id': payload['container_id'],
                'project_id': payload.get('project', GHC_PROJECT),
                'dataset': 'flywheel_views',
                'table': '_'.join(table_id_parts)
            }
        }

        if view_spec:
            job_payload['config']['json'] = view_spec
        elif payload.get('view_id'):
            job_payload['config']['view_id'] = payload['view_id']

        # TODO security - hide / get from user profile / TBD
        if payload.get('token'):
            job_payload['config']['token'] = payload['token']

        job = Queue.enqueue_job(job_payload, self.origin)
        job.insert()

        return {'_id': job.id_, 'destination': 'flywheel_views/{}'.format('_'.join(table_id_parts))}


def generate_service_account_token():
    if not GHC_KEY_JSON:
        return None
    scopes = ('https://www.googleapis.com/auth/cloud-platform',)
    credentials = Credentials.from_service_account_file(GHC_KEY_JSON, scopes=scopes)
    credentials.refresh(Request())
    return credentials.token


def format_query_result(result):
    total_studies = 0
    total_series = 0
    total_instances = 0
    studies = []

    for _, rows in itertools.groupby(result['rows'], key=lambda row: row['StudyInstanceUID']):
        total_studies += 1
        series = []
        for row in rows:
            total_series += 1
            total_instances += int(row['instance_count'])
            series.append({
                'SeriesDate': row['SeriesDate'],
                'SeriesTime': row['SeriesTime'],
                'SeriesInstanceUID': row['SeriesInstanceUID'],
                'SeriesDescription': row['SeriesDescription'],
                'instance_count': int(row['instance_count']),
            })

        # use last iterated `row` to get study properties
        # pylint: disable=undefined-loop-variable
        studies.append({
            'StudyDate': row.get('StudyDate'),
            'StudyTime': row.get('StudyTime'),
            'StudyInstanceUID': row.get('StudyInstanceUID'),
            'StudyDescription': row.get('StudyDescription'),
            'series_count': len(series),
            'series': sorted(series, key=lambda s: (s['SeriesDate'], s['SeriesTime']), reverse=True),
            'subject': row['PatientID'].rpartition('@')[0] or 'ex' + row['StudyID'],
        })

    return {
        'query_id': result['query_id'],
        'total_studies': total_studies,
        'total_series': total_series,
        'total_instances': total_instances,
        'study_count': len(studies),
        'studies': sorted(studies, key=lambda s: (s['StudyDate'], s['StudyTime']), reverse=True),
    }


class Session(requests.Session):
    def __init__(self, baseurl, headers=None, params=None):
        super(Session, self).__init__()
        self.baseurl = baseurl
        self.headers.update(headers or {})
        self.params.update(params or {})

    # pylint: disable=arguments-differ
    def request(self, method, url, **kwargs):
        return super(Session, self).request(method, self.baseurl + url, **kwargs)


class BigQuery(Session):
    def __init__(self, project, token):
        self.project = project
        super(BigQuery, self).__init__(
            'https://www.googleapis.com/bigquery/v2',
            headers={'Authorization': 'Bearer ' + token})

    def run_query(self, query):
        resp = self.post('/projects/{}/queries'.format(self.project), json={'query': query, 'useLegacySql': False})
        return self.get_resultset(resp)

    def get_query(self, query_id):
        resp = self.get('/projects/{}/queries/{}'.format(self.project, query_id))
        return self.get_resultset(resp)

    def get_resultset(self, response):
        if not response.ok:
            raise BigQueryError(response)
        resultset = response.json()
        fields = [field['name'] for field in resultset['schema']['fields']]
        return {'query_id': resultset['jobReference']['jobId'],
                'rows': (dict(zip(fields, (col['v'] for col in row['f']))) for row in resultset.get('rows', []))}

    def get_table(self, dataset, table):
        resp = self.get('/projects/{}/datasets/{}/tables/{}'.format(self.project, dataset, table))
        return resp.json()


class BigQueryError(APIException):
    def __init__(self, response):
        error = response.json()['error']
        super(BigQueryError, self).__init__(msg=error['message'])
        self.status_code = error['code']
