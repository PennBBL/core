from .report import Report

from .. import config

class SiteReport(Report):
    """
    Report of statistics about the site, generated by Site Managers

    Report includes:
      - number of groups
      - number of projects per group
      - number of sessions per group
    """

    def user_can_generate(self, uid):
        """
        User generating report must be superuser
        """
        if config.db.users.count({'_id': uid, 'root': True}) > 0:
            return True
        return False

    def build(self):
        report = {}

        groups = config.db.groups.find({})
        report['group_count'] = groups.count()
        report['groups'] = []

        for g in groups:
            group = {}
            group['label'] = g.get('label')

            project_ids = [p['_id'] for p in config.db.projects.find({'group': g['_id'], 'deleted': {'$exists': False}}, [])]
            group['project_count'] = len(project_ids)

            group['session_count'] = config.db.sessions.count({'project': {'$in': project_ids}, 'deleted': {'$exists': False}})
            report['groups'].append(group)

        return report