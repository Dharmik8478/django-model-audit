from django.apps import AppConfig, apps
import django.db.models.options as options
from django.db import connection

from audit_trail.signals import audit_ready

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('managed_fields', 'extra_fields',
                                                         'display_format', 'parent_field',
                                                         'sensitive_fields')
class AuditTrailConfig(AppConfig):
    name = 'audit_trail'
    def ready(self):
        tables = connection.introspection.table_names()
        Entity = apps.get_model('audit_trail.Entity')
        if Entity._meta.db_table in tables:
            audit_ready.send(sender=self.__class__)

