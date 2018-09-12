from google.cloud import bigquery

from .. import config
from ..auth import require_login
from ..web import base

log = config.log


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
    def query_result(self, job_id):
        # Just an example endpoint how to retrieve the results of a job
        query_job = config.bq_client.get_job(job_id)
        return self._prepare_response(query_job)

    @require_login
    def post(self):
        payload = self.request.json_body

        dataset_ref = config.bq_client.dataset(payload['dataset'])
        table_ref = dataset_ref.table(payload['table'])
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
            'SELECT {fields} FROM `{dataset}.{table}` '
            'WHERE {where} GROUP BY {fields} '
            'LIMIT 100'.format(fields=', '.join(group_by_fields), **payload))

        query_job = config.bq_client.query(
            query,
            # Location must match that of the dataset(s) referenced in the query.
            location='US')  # API request - starts the query

        return self._prepare_response(query_job)
