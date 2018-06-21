import dateutil
import pymongo
import pytz

from .report import Report

from .. import config
from .. import util

from ..web.errors import APIReportParamsException
from ..web.request import AccessTypeList


class AccessLogReport(Report):
    """
    Report of the last <limit> logs in the access log.

    Specify a uid to only return logs for a specific user.
    Specify a date range to only return logs in that range.

    Report includes:
      - action completed
      - user that took action
      - information about the session/project/group in which the action took place
    """

    # What to name csvs generated from this report
    filename = 'accesslog'

    columns = [
        "_id",
        "timestamp",
        "ip",
        "access_type",
        "origin.id",
        "origin.email",
        "origin.method",
        "origin.name",
        "origin.type",
        "origin.via.type",
        "origin.via.id",
        "context.group.id",
        "context.group.label",
        "context.project.id",
        "context.project.label",
        "context.subject.id",
        "context.subject.label",
        "context.session.id",
        "context.session.label",
        "context.acquisition.id",
        "context.acquisition.label",
        "context.analysis.id",
        "context.analysis.label",
        "context.collection.id",
        "context.collection.label",
        "context.file.name",
        "context.ticket_id",
        "request_method",
        "request_path"
    ]

    def __init__(self, params):
        """
        Initialize an Access Log Report

        Possible keys in :params:
        :start_date:    ISO formatted timestamp
        :end_date:      ISO formatted timestamp
        :uid:           user id of the target user
        :limit:         number of records to return
        :subject:       subject code of session accessed
        :access_type:  list of access_types to filter logs
        :csv:           Boolean if user wants csv file
        """

        super(AccessLogReport, self).__init__(params)

        start_date = params.get('start_date')
        end_date = params.get('end_date')
        uid = params.get('user')
        limit= params.get('limit', 100)
        subject = params.get('subject', None)
        project = params.get('project', None)
        access_types = params.getall('access_type')

        if start_date:
            start_date = dateutil.parser.parse(start_date)
        if end_date:
            end_date = dateutil.parser.parse(end_date)
        if end_date and start_date and end_date < start_date:
            raise APIReportParamsException('End date {} is before start date {}'.format(end_date, start_date))
        if uid and not util.is_user_id(uid):
            raise APIReportParamsException('Invalid user.')
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            raise APIReportParamsException('Limit must be an integer greater than 0.')
        if limit < 1:
            raise APIReportParamsException('Limit must be an integer greater than 0.')
        elif limit > 10000:
            raise APIReportParamsException('Limit exceeds 10,000 entries, please contact admin to run script.')
        for access_type in access_types:
            if access_type not in AccessTypeList:
                raise APIReportParamsException('Not a valid access type')

        self.start_date     = start_date
        self.end_date       = end_date
        self.uid            = uid
        self.limit          = limit
        self.subject        = subject
        self.project        = project
        self.access_types   = access_types

    def user_can_generate(self, uid):
        """
        User generating report must be superuser
        """
        if config.db.users.count({'_id': uid, 'root': True}) > 0:
            return True
        return False

    def build(self):
        query = {}

        if self.uid:
            query['origin.id'] = self.uid
        if self.start_date or self.end_date:
            query['timestamp'] = {}
        if self.start_date:
            query['timestamp']['$gte'] = self.start_date
        if self.end_date:
            query['timestamp']['$lte'] = self.end_date
        if self.subject:
            query['context.subject.label'] = self.subject
        if self.project:
            query['context.project.id'] = self.project
        if self.access_types:
            query['access_type'] = {'$in': self.access_types}

        return config.log_db.access_log.find(query).limit(self.limit).sort('timestamp', pymongo.DESCENDING).batch_size(1000)

    def format_row(self, row, out_format):
        if out_format == 'csv' or out_format == 'tsv':
            # Format timestamp as ISO UTC
            row['timestamp'] = pytz.timezone('UTC').localize(row['timestamp']).isoformat()
