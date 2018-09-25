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
        cols = []

        for field in query_job.result().schema:
            cols.append(field.name)

        response = {
            'jobId': query_job.job_id,
            'rows': [],
            'columns': cols
        }

        for row in query_job:  # API request - fetches results
            # Row values can be accessed by field name or index
            result_row = []
            for field in cols:
                result_row.append(row[field])
            response['rows'].append(result_row)
        return response

    @require_login
    def import_job(self):
        # Just an example endpoint how to retrieve the results of a job
        query_job_id = self.request.json_body['jobId']
        g_project = self.request.json_body['project']
        location = self.request.json_body['location']
        dataset = self.request.json_body['dataset']
        store = self.request.json_body['store']
        query_job = config.bq_client.get_job(query_job_id)

        series_to_import = []

        for row in query_job:
            series_to_import.append('%s/%s' % (row['StudyInstanceUID'], row['SeriesInstanceUID']))

        gear_doc = config.db.gears.find_one({
            'gear.name': 'ghc-import'
        }, sort=[('gear.version', -1)])

        project = config.db.projects.find_one({'label': 'ghc'})
        if not project:
            self.abort(404, "Project with label 'ghc' is required")

        job_payload = {
            'gear_id': gear_doc['_id'],
            'destination': {
                'type': 'project',
                'id': project['_id']
            },
            'config': {
                'series': series_to_import,
                'project': g_project,
                'location': location,
                'dataset': dataset,
                'dicomstore': store
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

        dataset_ref = config.bq_client.dataset(payload['dataset'])
        table_ref = dataset_ref.table(payload['store'])
        table = config.bq_client.get_table(table_ref)

        req_group_by_fields = [
            bigquery.SchemaField('StudyInstanceUID', 'STRING', 'NULLABLE'),
            bigquery.SchemaField('SeriesInstanceUID', 'STRING', 'NULLABLE'),
            bigquery.SchemaField('StudyDate', 'DATE', 'NULLABLE'),
            bigquery.SchemaField('SeriesDescription', 'STRING', 'NULLABLE'),
            bigquery.SchemaField('StudyDescription', 'STRING', 'NULLABLE')
        ]

        group_by_fields = []

        for field in req_group_by_fields:
            if field in table.schema:
                group_by_fields.append(field.name)

        query = (
            'SELECT {fields} FROM `{dataset}.{store}` '
            'WHERE {where} GROUP BY {fields} '
            'LIMIT 100'.format(fields=', '.join(group_by_fields), **payload))

        query_job = config.bq_client.query(
            query,
            # Location must match that of the dataset(s) referenced in the query.
            location='US')  # API request - starts the query

        return self._prepare_response(query_job)
