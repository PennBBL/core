import webapp2
import webapp2_extras.routes

from .download                          import Download
from .handlers.abstractcontainerhandler import AbstractContainerHandler
from .handlers.collectionshandler       import CollectionsHandler
from .handlers.confighandler            import Config, Version
from .handlers.containerhandler         import ContainerHandler
from .handlers.dataexplorerhandler      import DataExplorerHandler, QueryHandler
from .handlers.devicehandler            import DeviceHandler
from .handlers.gcphandler               import GCPHandler, GHCHandler, BigQueryHandler
from .handlers.grouphandler             import GroupHandler
from .handlers.listhandler              import FileListHandler, NotesListHandler, PermissionsListHandler, TagsListHandler
from .handlers.modalityhandler          import ModalityHandler
from .handlers.refererhandler           import AnalysesHandler
from .handlers.resolvehandler           import ResolveHandler
from .handlers.roothandler              import RootHandler
from .handlers.schemahandler            import SchemaHandler
from .handlers.userhandler              import UserHandler
from .jobs.handlers                     import BatchHandler, JobsHandler, JobHandler, GearsHandler, GearHandler, RulesHandler, RuleHandler
from .metrics.handler                   import MetricsHandler
from .upload                            import Upload
from .reports.handler                   import ReportHandler
from .data_views.handlers               import DataViewHandler
from .web.base                          import RequestHandler
from . import config


log = config.log

routing_regexes = {

    # Group ID: 2-32 characters of form [0-9a-z.@_-]. Start and ends with alphanum.
    'gid': '[0-9a-z][0-9a-z.@_-]{0,30}[0-9a-z]',

    # User ID: any length, [0-9a-z.@_-]
    'uid': '[0-9a-zA-Z.@_-]*',

    # Object ID: 24-character hex
    'oid': '[0-9a-f]{24}',

    # Container name
    'cname': 'groups|projects|subjects|sessions|acquisitions|collections|analyses',

    # Tag name
    'tag': '[^/]{1,32}',

    # Filename
    'fname': '.+',

    # Filename/info
    'finfo': '.+(?=/info)',

    # Filename/classification
    'fclass': '.+(?=/classification)',

    # Schema path
    'schema': r'[^/.]{3,60}/[^/.]{3,60}\.json'
}


def route(path, target, h=None, m=None, name=None):

    # https://webapp2.readthedocs.io/en/latest/api/webapp2.html#webapp2.Route
    return webapp2.Route(
        # re.compile(path)
        path.format(**routing_regexes),
        target,
        handler_method=h,
        methods=m,
        name=name
    )

def prefix(path, routes):

    # https://webapp2.readthedocs.io/en/latest/api/webapp2_extras/routes.html#webapp2_extras.routes.PathPrefixRoute
    return webapp2_extras.routes.PathPrefixRoute(
        path.format(**routing_regexes),
        routes
    )

endpoints = [
    route('/api',                  RootHandler),
    prefix('/api', [

        # System configuration

        route('/config',           Config,              m=['GET']),
        route('/config.js',        Config,  h='get_js', m=['GET']),
        route('/version',          Version,             m=['GET']),


        # General-purpose upload & download

        route('/download',                                      Download, h='download',              m=['GET', 'POST']),
        route('/download/summary',                              Download, h='summary',               m=['POST']),
        route('/upload/<strategy:label|uid|uid-match|reaper>',  Upload,   h='upload',                m=['POST']),
        route('/clean-packfiles',                               Upload,   h='clean_packfile_tokens', m=['POST']),
        route('/engine',                                        Upload,   h='engine',                m=['POST']),


        # Top-level endpoints
        route('/login',                                         RequestHandler, h='log_in',         m=['POST']),
        route('/login/saml',                                    RequestHandler, h='saml_log_in',    m=['GET']),
        route('/auth/status',                                   RequestHandler, h='auth_status',    m=['GET']),
        route('/logout',                                        RequestHandler, h='log_out',        m=['POST']),
        route('/lookup',                                        ResolveHandler, h='lookup',         m=['POST']),
        route('/resolve',                                       ResolveHandler, h='resolve',        m=['POST']),
        route('/schemas/<schema:{schema}>',                     SchemaHandler,                      m=['GET']),
        route('/report/<report_type:site|project|accesslog|usage>',   ReportHandler,                m=['GET']),
        route('/report/accesslog/types',                        ReportHandler,  h='get_types',      m=['GET']),


        # Search
        route('/dataexplorer/search',                   DataExplorerHandler,   h='search',                 m=['POST']),
        route('/dataexplorer/facets',                   DataExplorerHandler,   h='get_facets',             m=['POST']),
        route('/dataexplorer/search/fields',            DataExplorerHandler,   h='search_fields',          m=['POST']),
        route('/dataexplorer/search/fields/aggregate',  DataExplorerHandler,   h='aggregate_field_values', m=['POST']),
        route('/dataexplorer/search/nodes',             DataExplorerHandler,   h='get_nodes',              m=['POST']),
        route('/dataexplorer/index/fields',             DataExplorerHandler,   h='index_field_names',      m=['POST']),
        route('/dataexplorer/search/training',                DataExplorerHandler,   h='save_training_set',      m=['POST']),

        # Search Saving
        route('/dataexplorer/queries',                            QueryHandler,                                m=['POST']),
        route('/dataexplorer/queries',                            QueryHandler,     h='get_all',               m=['GET']),
        route('/dataexplorer/queries/<sid:{oid}>',                QueryHandler,                                m=['GET','DELETE']),
        route('/dataexplorer/queries/<sid:{oid}>',                QueryHandler,                                m=['PUT']),

        # Users

        route( '/users',                   UserHandler, h='get_all', m=['GET']),
        route( '/users',                   UserHandler,              m=['POST']),
        prefix('/users', [
            route('/self',                 UserHandler, h='self',            m=['GET']),
            route('/self/avatar',          UserHandler, h='self_avatar',     m=['GET']),
            route('/self/key',             UserHandler, h='generate_api_key',m=['POST']),

            route('/<_id:{uid}>',                       UserHandler),
            route('/<uid:{uid}>/groups',                GroupHandler,                h='get_all',               m=['GET']),
            route('/<uid:{uid}>/avatar',                UserHandler,                 h='avatar',                m=['GET']),
            route('/<uid:{uid}>/reset-registration',    UserHandler,                 h='reset_registration',    m=['POST']),
            route('/<uid:{uid}>/<cont_name:{cname}>',   ContainerHandler, h='get_all_for_user', m=['GET']),

        ]),


        # Jobs & gears

        route( '/jobs',                    JobsHandler),
        prefix('/jobs', [
            route('/next',                 JobsHandler, h='next',       m=['GET']),
            route('/stats',                JobsHandler, h='stats',      m=['GET']),
            route('/pending',              JobsHandler, h='pending',    m=['GET']),
            route('/reap',                 JobsHandler, h='reap_stale', m=['POST']),
            route('/add',                  JobsHandler, h='add',        m=['POST']),
            route('/<:[^/]+>',             JobHandler),
            route('/<:[^/]+>/config.json', JobHandler,  h='get_config'),
            route('/<:[^/]+>/retry',       JobHandler,  h='retry',         m=['POST']),
            route('/<:[^/]+>/logs',        JobHandler,  h='get_logs',      m=['GET']),
            route('/<:[^/]+>/logs/text',   JobHandler,  h='get_logs_text', m=['GET']),
            route('/<:[^/]+>/logs/html',   JobHandler,  h='get_logs_html', m=['GET']),
            route('/<:[^/]+>/logs',        JobHandler,  h='add_logs',      m=['POST']),
            route('/<:[^/]+>/prepare-complete',     JobHandler,  h='prepare_complete',     m=['POST']),
            route('/<:[^/]+>/accept-failed-output', JobHandler,  h='accept_failed_output', m=['POST']),
            route('/<:[^/]+>/profile',     JobHandler,  h='update_profile', m=['PUT']),
        ]),
        route('/gears',                                  GearsHandler),

        # New upload flow
        route('/gears/prepare-add',                      GearsHandler, h='prepare_add',     m=['POST']),
        route('/gears/ticket/<_id:[^/]+>',               GearsHandler, h='get_ticket',      m=['GET']),
        route('/gears/my-tickets',                       GearsHandler, h='get_own_tickets', m=['GET']),
        route('/gears/save',                             GearsHandler, h='save',            m=['POST']),

        # Old upload flow (deprecated)
        route('/gears/check',                            GearsHandler, h='check',           m=['POST']),
        route('/gears/temp',                             GearHandler,  h='upload',          m=['POST']),

        # Old download flow (stays forever)
        route('/gears/temp/<cid:{oid}>',                 GearHandler,  h='download',        m=['GET']),

        prefix('/gears', [
            route('/<:[^/]+>',                           GearHandler),
            route('/<:[^/]+>/invocation',                GearHandler, h='get_invocation'),
            route('/<:[^/]+>/suggest/<:{cname}|subjects>/<:[^/]+>', GearHandler, h='suggest'),
            route('/<:[^/]+>/context/<:{cname}>/<:{oid}>', GearHandler, h='get_context', m=['GET']),
        ]),

        # Batch jobs

        route('/batch',                 BatchHandler,   h='get_all',        m=['GET']),
        route('/batch',                 BatchHandler,                       m=['POST']),
        prefix('/batch', [
            route('/jobs',              BatchHandler,   h='post_with_jobs', m=['POST']),
            route('/<:[^/]+>',          BatchHandler,   h='get',            m=['GET']),
            route('/<:[^/]+>/run',      BatchHandler,   h='run',            m=['POST']),
            route('/<:[^/]+>/cancel',   BatchHandler,   h='cancel',         m=['POST']),
        ]),


        # Devices

        route( '/devices',              DeviceHandler, h='get_all',    m=['GET']),
        route( '/devices',              DeviceHandler,                 m=['POST']),
        prefix('/devices', [
            route('/status',            DeviceHandler, h='get_status', m=['GET']),
            route('/self',              DeviceHandler, h='put_self',   m=['PUT']),
            route('/<device_id:{oid}>', DeviceHandler,                 m=['GET', 'DELETE']),
            route('/logging/<filename:{fname}>', DeviceHandler, h='serve_logging_credentials', m=['GET']),
        ]),


        # Modalities

        route( '/modalities',               ModalityHandler, h='get_all',    m=['GET']),
        route( '/modalities',               ModalityHandler,                 m=['POST']),
        prefix('/modalities', [
            route('/<modality_name:[^/]+>', ModalityHandler,                 m=['GET', 'PUT', 'DELETE']),
        ]),


        # Site

        route('/<cid:site>/rules',              RulesHandler,          m=['GET', 'POST']),
        route('/<cid:site>/rules/<rid:{oid}>',  RuleHandler,           m=['GET', 'PUT', 'DELETE']),


        # Data views

        prefix('/containers/<parent:{gid}|{oid}|{uid}>', [
            route('/views', DataViewHandler, h='list_views',            m=['GET']),
            route('/views', DataViewHandler,                            m=['POST']),
        ]),

        prefix('/views', [
            route('/data',             DataViewHandler, h='execute_adhoc',     m=['POST']),
            route('/save',             DataViewHandler, h='execute_and_save',  m=['POST']),
            route('/columns',          DataViewHandler, h='get_columns',       m=['GET']),
            route('/<_id:{oid}>',      DataViewHandler,                        m=['GET', 'DELETE', 'PUT']),
            route('/<_id:{oid}>/data', DataViewHandler, h='execute_saved',     m=['GET'])
        ]),


        # Abstract container

        route('/containers/<cid:{gid}|{oid}><extra:.*>', AbstractContainerHandler, h='handle'),


        # Groups

        route('/groups',             GroupHandler, h='get_all', m=['GET']),
        route('/groups',             GroupHandler,              m=['POST']),
        route('/groups/<_id:{gid}>', GroupHandler,              m=['GET', 'DELETE', 'PUT']),

        prefix('/<cont_name:groups>', [
            route('/<cid:{gid}>/<list_name:permissions>',                          PermissionsListHandler,     m=['POST']),
            route('/<cid:{gid}>/<list_name:permissions>/<_id:{uid}>', PermissionsListHandler,     m=['GET', 'PUT', 'DELETE']),

            route('/<cid:{gid}>/<list_name:tags>',                           TagsListHandler, m=['POST']),
            route('/<cid:{gid}>/<list_name:tags>/<value:{tag}>',             TagsListHandler, m=['GET', 'PUT', 'DELETE']),
            route('/<cid:{gid}>/<sub_cont_name:{cname}|all>/analyses',       AnalysesHandler, h='get_all',       m=['GET']),
        ]),


        # Projects

        prefix('/projects', [
            route('/groups',               ContainerHandler, h='get_groups_with_project',      m=['GET']),
            route('/recalc',               ContainerHandler, h='calculate_project_compliance', m=['POST']),
            route('/<cid:{oid}>/template', ContainerHandler, h='set_project_template',         m=['POST']),
            route('/<cid:{oid}>/template', ContainerHandler, h='delete_project_template',      m=['DELETE']),
            route('/<cid:{oid}>/recalc',   ContainerHandler, h='calculate_project_compliance', m=['POST']),
            route('/<cid:{oid}>/rules',    RulesHandler,                                       m=['GET', 'POST']),
            route('/<cid:{oid}>/rules/<rid:{oid}>',  RuleHandler,                              m=['GET', 'PUT', 'DELETE']),
        ]),


        # Sessions

        prefix('/sessions', [
            route('/<cid:{oid}>/jobs',          ContainerHandler, h='get_jobs',     m=['GET']),
            route('/<cid:{oid}>/subject',       ContainerHandler, h='get_subject',  m=['GET']),
        ]),


        # Collections

        route( '/collections',                 CollectionsHandler, h='get_all',                    m=['GET']),
        route( '/collections',                 CollectionsHandler,                                 m=['POST']),
        prefix('/collections', [
            route('/curators',                 CollectionsHandler, h='curators',                   m=['GET']),
            route('/<cid:{oid}>',              CollectionsHandler,                                 m=['GET', 'PUT', 'DELETE']),
            route('/<cid:{oid}>/sessions',     CollectionsHandler, h='get_sessions',               m=['GET']),
            route('/<cid:{oid}>/acquisitions', CollectionsHandler, h='get_acquisitions',           m=['GET']),
        ]),


        # Collections / Projects

        prefix('/<cont_name:collections|projects|dataexplorer/queries>', [
            prefix('/<cid:{oid}>', [
                route('/<list_name:permissions>',                          PermissionsListHandler, m=['POST']),
                route('/<list_name:permissions>/<_id:{uid}>',              PermissionsListHandler, m=['GET', 'PUT', 'DELETE']),
            ]),
        ]),


        # Analyses
        route( '/analyses/<_id:{oid}>',                      AnalysesHandler,  m=['GET']),
        prefix('/analyses/<_id:{oid}>', [
            route('/files',                                       AnalysesHandler, h='upload',      m=['POST']),
            route('/<filegroup:inputs|files>',                    AnalysesHandler, h='download',    m=['GET']),
            route('/<filegroup:inputs|files>/<filename:{fname}>', AnalysesHandler, h='download',    m=['GET']),
            route('/info',                                        AnalysesHandler, h='modify_info', m=['POST']),
        ]),
        prefix('/<:{cname}>/<:{oid}>/<cont_name:analyses>/<cid:{oid}>', [
            route('/<list_name:notes>',                         NotesListHandler,               m=['POST']),
            route('/<list_name:notes>/<_id:{oid}>',             NotesListHandler, name='notes', m=['GET', 'PUT', 'DELETE']),
        ]),


        # Containers

        route( '/<cont_name:{cname}>', ContainerHandler, name='cont_list', h='get_all', m=['GET']),
        route( '/<cont_name:{cname}>', ContainerHandler,                                m=['POST']),
        prefix('/<cont_name:{cname}>', [
            route( '/<cid:{oid}>',     ContainerHandler,                                m=['GET','PUT','DELETE']),
            prefix('/<cid:{oid}>', [

                route( '/info',                   ContainerHandler, h='modify_info', m=['POST']),
                route( '/<subject:subject>/info', ContainerHandler, h='modify_info', m=['POST']),

                route('/<list_name:tags>',               TagsListHandler, m=['POST']),
                route('/<list_name:tags>/<value:{tag}>', TagsListHandler, m=['GET', 'PUT', 'DELETE']),

                route('/packfile-start',                        FileListHandler, h='packfile_start',        m=['POST']),
                route('/packfile',                              FileListHandler, h='packfile',              m=['POST']),
                route('/packfile-end',                          FileListHandler, h='packfile_end'),

                route('/<list_name:files>',                     FileListHandler,                            m=['POST']),
                route('/<list_name:files>/<name:{finfo}>/info',      FileListHandler, h='get_info',              m=['GET']),
                route('/<list_name:files>/<name:{finfo}>/info',      FileListHandler, h='modify_info',           m=['POST']),
                route('/<list_name:files>/<name:{fclass}>/classification',     FileListHandler, h='modify_classification', m=['POST']),
                route('/<list_name:files>/<name:{fname}>',      FileListHandler,                            m=['GET', 'PUT', 'DELETE']),

                route( '/<sub_cont_name:{cname}|all>/analyses', AnalysesHandler, h='get_all', m=['GET']),
                route( '/analyses',                             AnalysesHandler, h='get_all', m=['GET']),
                route( '/analyses',                             AnalysesHandler,              m=['POST']),
                prefix('/analyses', [
                    route('/<_id:{oid}>',                                             AnalysesHandler,               m=['GET', 'PUT', 'DELETE']),
                    route('/<_id:{oid}>/files',                                       AnalysesHandler, h='upload',   m=['POST']),
                    route('/<_id:{oid}>/<filegroup:inputs|files>',                    AnalysesHandler, h='download', m=['GET']),
                    route('/<_id:{oid}>/<filegroup:inputs|files>/<filename:{fname}>', AnalysesHandler, h='download', m=['GET']),
                ]),

                route('/<list_name:notes>',             NotesListHandler,               m=['POST']),
                route('/<list_name:notes>/<_id:{oid}>', NotesListHandler, name='notes', m=['GET', 'PUT', 'DELETE']),
            ])
        ]),

        # Metrics
        route('/metrics', MetricsHandler, m=['GET']),

        # Misc (to be cleaned up later)

        route('/<par_cont_name:groups>/<par_id:{gid}>/<cont_name:projects>', ContainerHandler, h='get_all', m=['GET']),
        route('/<par_cont_name:{cname}>/<par_id:{oid}>/<cont_name:{cname}>', ContainerHandler, h='get_all', m=['GET']),

        # Google Cloud Platform
        prefix('/gcp', [
            route('/token',     GCPHandler, h='generate_token', m=['GET']),
            route('/config',    GCPHandler, h='get_default_config', m=['GET']),
            # Google Healthcare
            prefix('/hc', [
                route('/query',     GHCHandler, h='run_query',          m=['POST']),
                route('/details',   GHCHandler, h='run_details_query',  m=['POST']),
                route('/import',    GHCHandler, h='run_import',         m=['POST']),
                route('/jobs',      GHCHandler, h='get_jobs',           m=['GET']),
                route('/statistic', GHCHandler, h='run_statistics',     m=['POST']),
                route('/schema',    GHCHandler, h='get_schema',         m=['POST']),
            ]),
            # Google BigQuery
            prefix('/bq', [
                route('/export',    BigQueryHandler,    h='export_view',         m=['POST']),
            ]),
        ]),
    ]),
]
