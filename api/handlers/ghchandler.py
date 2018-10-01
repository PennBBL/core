from google.auth.transport.requests import Request
from google.cloud import bigquery
from google.oauth2 import service_account

from .. import config
from ..auth import require_login
from ..jobs.queue import Queue
from ..web import base

log = config.log

SCOPES = ('https://www.googleapis.com/auth/cloud-platform', )


class GoogleHealthcareHandler(base.RequestHandler):

    @staticmethod
    def _prepare_response(query_job):
        result = {
            'TotalNumberOfStudies': 0,
            'TotalNumberOfSeries': 0,
            'TotalNumberOfInstances': 0,
            'Studies': []
        }

        curr_study = {}
        for row in query_job:
            if curr_study.get('StudyInstanceUID') == row.get('StudyInstanceUID'):
                curr_study['series'].append(
                    {
                        'SeriesInstanceUID': row.get('SeriesInstanceUID'),
                        'SeriesDescription': row.get('SeriesDescription'),
                        'NumberOfInstances': row.get('NumberOfInstances'),
                    }
                )
                curr_study['NumberOfSeries'] += 1
            else:
                if curr_study:
                    result['Studies'].append(curr_study)
                    result['TotalNumberOfSeries'] += len(curr_study['series'])

                curr_study = {
                    'StudyInstanceUID': row.get('StudyInstanceUID'),
                    'StudyDescription': row.get('StudyDescription'),
                    'NumberOfSeries': 1,
                    'StudyDate': row.get('StudyDate'),
                    'series': [
                        {
                            'SeriesInstanceUID': row.get('SeriesInstanceUID'),
                            'SeriesDescription': row.get('SeriesDescription'),
                            'NumberOfInstances': row.get('NumberOfInstances'),
                        }
                    ]
                }

            result['TotalNumberOfInstances'] += row.get('NumberOfInstances')

        if curr_study:
            result['Studies'].append(curr_study)
            result['TotalNumberOfSeries'] += len(curr_study['series'])

        result['TotalNumberOfStudies'] = len(result['Studies'])
        result['JobId'] = query_job.job_id

        return result

    @require_login
    def import_job(self):
        payload = self.request.json_body
        import_level = payload['level']

        query_job_id = payload.get('jobId')
        uids = payload.get('uids') or []
        exclude = payload['exclude'] or []

        to_import = []

        if query_job_id:
            query_job = config.bq_client.get_job(query_job_id)

            for row in query_job:
                uid_field_name = 'SeriesInstanceUID' if import_level == 'series' else 'StudyInstanceUID'
                if row[uid_field_name] not in exclude:
                    to_import.append(row[uid_field_name])
        else:
            for uid in set(uids) - set(exclude):
                if import_level == 'series':
                    to_import.append(uid)

        if not to_import:
            return self.abort(400, 'Nothing to import')

        gear_doc = config.db.gears.find_one({
            'gear.name': 'ghc-import'
        }, sort=[('gear.version', -1)])

        if not gear_doc:
            return self.abort(404, 'ghc-import gear is not installed, you have to install it to use this feature')

        project = config.db.projects.find_one({'label': 'ghc'})
        if not project:
            return self.abort(404, "Project with label 'ghc' is required")

        job_payload = {
            'gear_id': gear_doc['_id'],
            'destination': {
                'type': 'project',
                'id': project['_id']
            },
            'config': {
                'uids': to_import,
                'level': import_level,
                'project': payload['project'],
                'location': payload['location'],
                'dataset': payload['dataset'],
                'dicomstore': payload['store'],
                'log-level': payload['log-level']
            }
        }

        job = Queue.enqueue_job(job_payload, self.origin)
        job.insert()

        return {'_id': job.id_}

    @require_login
    def get_ghc_token(self):
        credentials = service_account.Credentials.from_service_account_file(config.ghc_key_path, scopes=SCOPES)

        credentials.refresh(Request())
        token = credentials.token

        return {'token': token}

    @require_login
    def post(self):
        payload = self.request.json_body
        print(payload)

        dataset_ref = config.bq_client.dataset(payload['dataset'])
        table_ref = dataset_ref.table(payload['store'])
        table = config.bq_client.get_table(table_ref)

        req_group_by_fields = [
            bigquery.SchemaField('StudyInstanceUID', 'STRING', 'NULLABLE'),
            bigquery.SchemaField('SeriesInstanceUID', 'STRING', 'NULLABLE'),
            bigquery.SchemaField('StudyDate', 'DATE', 'NULLABLE'),
            bigquery.SchemaField('StudyTime', 'TIME', 'NULLABLE'),
            bigquery.SchemaField('SeriesDescription', 'STRING', 'NULLABLE'),
            bigquery.SchemaField('StudyDescription', 'STRING', 'NULLABLE')
        ]

        group_by_fields = []

        for field in req_group_by_fields:
            if field in table.schema:
                group_by_fields.append(field.name)

        query = (
            'SELECT {fields}, '
            'COUNT(DISTINCT SOPInstanceUID) AS NumberOfInstances '
            'FROM `{dataset}.{store}` '
            'WHERE {where} GROUP BY {fields} '
            'ORDER BY StudyDate, StudyTime, StudyInstanceUID '
            'LIMIT 100'.format(fields=', '.join(group_by_fields), **payload))

        query_job = config.bq_client.query(
            query,
            # Location must match that of the dataset(s) referenced in the query.
            location=payload['location'])  # API request - starts the query

        return self._prepare_response(query_job)
