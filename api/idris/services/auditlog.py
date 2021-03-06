import datetime
import logging

from zope.interface import implementer
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from idris.interfaces import IAuditLogService

@implementer(IAuditLogService)
class BQAuditLog(object):
    def __init__(self, uri, prefix):
        self.ds_name = prefix
        app_credentials = uri.split('#', 1)[1]
        self.client=bigquery.Client().from_service_account_json(app_credentials)
        self.ds_ref = self.client.dataset(self.ds_name)
        field = bigquery.SchemaField
        self.schema = [
            field('action', 'STRING', mode='REQUIRED'),
            field('work_id', 'INTEGER', mode='REQUIRED'),
            field('user_id', 'STRING', mode='REQUIRED'),
            field('created', 'TIMESTAMP', mode='REQUIRED'),
            field('context_id', 'INTEGER'),
            field('message', 'STRING'),
            field('value', 'STRING')
        ]

    def table_ref(self, name):
        return self.ds_ref.table('%s_auditlog' % name)

    def has_log(self, name):
        try:
            self.client.get_table(self.table_ref(name))
        except NotFound:
            # make sure that the dataset exists
            try:
                self.client.get_dataset(self.ds_ref)
            except NotFound:
                raise ValueError(
                    'Missing BigQuery dataset: %s' % self.ds_name)
            return False
        return True

    def create_log(self, name):
        table = bigquery.Table(self.table_ref(name), schema=self.schema)
        table.time_partitioning = bigquery.table.TimePartitioning(
            field='created')
        table.clustering_fields=['work_id']
        table = self.client.create_table(table)
        return True

    def append(self,
               log_name,
               action,
               work_id,
               user_id,
               context_id=None,
               message=None,
               created=None,
               value=None):
        if created is None:
            created = datetime.datetime.utcnow()
        if isinstance(user_id, int):
            user_id = '%s' % user_id
        created = created.strftime('%Y-%m-%dT%H:%M:%S')
        rows = [(action, work_id, user_id, created, context_id, message, value)]
        try:
            result = self.client.insert_rows(
                self.table_ref(log_name), rows, selected_fields=self.schema)
        except NotFound:
            logging.warning('Appending to auditlog: %s failed: no such log' % log_name)
            return False

        if result and result[0].get('errors'):
            logging.warning('Appending to auditlog: %s failed: %s' % (
                log_name, result[0]['errors']))
            return False
        return True

    def work_history(self, log_name, work_id):
        work_id = int(work_id)
        query = ('SELECT * FROM `%s.%s_auditlog` '
                 'WHERE work_id = %s ORDER BY created DESC' % (
                     self.ds_name, log_name, work_id))
        query_job = self.client.query(query, location='EU')
        for row in query_job:
            yield dict(row)

def auditlog_factory(registry, repository_namespace):
    config_url = registry.settings['auditlog.url']
    proto = config_url.split('://')[0]
    if not 'idris.google_application_credentials' in registry.settings:
        return

    if config_url == 'bigquery://':
        config_url = 'bigquery://%s#%s' % (
            registry.settings['idris.google_cloud_project'],
            registry.settings['idris.google_application_credentials'])
    CacheImpl = registry.queryUtility(IAuditLogService, proto)
    prefix = ('%s-%s' % (registry.settings['idris.app_prefix'],
                         repository_namespace)).replace('-', '_')
    return CacheImpl(config_url, prefix)



def includeme(config):
    config.registry.registerUtility(
        BQAuditLog, IAuditLogService, 'bigquery')
