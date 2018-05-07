'''
Created on 02-Feb-2017

@author: dharmikp
'''
import logging
import getpass

from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils import six
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from audit_trail.common import DictDiffer
from audit_trail.signals import audit_ready, audit_m2m_ready
from audit_trail.apps import AuditTrailConfig
from audit_trail.middleware import AuditMiddleware

LOGGER = logging.getLogger('audit_log')

from django.db.models.signals import (pre_save, class_prepared, post_save,
                                        m2m_changed, post_delete)

from audit_trail.models import (Entity, Field, StorageBin, FieldDiff,
                                        ContentType, Xaction,
                                        XactionParentEntityChildFieldMap,
                                        ParentEntityChildFieldMap)


class AuditManager(models.QuerySet):

    def update(self, *args, **kwargs):
        prev_val_dict ={}
        curr_val_dict = {}
        for obj in self:
            prev_val, curr_val = self._get_audit_values(obj, kwargs)
            prev_val_dict.update({obj.pk: prev_val})
            curr_val_dict.update({obj.pk: curr_val})

        return_val = super(AuditManager, self).update(*args, **kwargs)

        for key in prev_val_dict.keys():
            audit_trail = CoreAudit(self.model, obj, 'U',
                                    prev_val_dict.get(key),
                                    curr_val_dict.get(key)
                                    )
            audit_trail.create_audit()
        return return_val

    def update_or_create(self, *args, defaults=None, **kwargs):
        """
        Looks up an object with the given kwargs, updating one with defaults
        if it exists, otherwise creates a new one.
        Returns a tuple (object, created), where created is a boolean
        specifying whether an object was created.
        """
        defaults = defaults or {}
        lookup, params = self._extract_model_params(defaults, **kwargs)
        self._for_write = True
        with transaction.atomic(using=self.db):
            try:
                obj = self.select_for_update().get(**lookup)
            except self.model.DoesNotExist:
                obj, created = self._create_object_from_params(lookup, params)
                if created:
                    prev_val, curr_val = self._get_audit_values(obj, {**defaults, **kwargs})
                    audit_trail = CoreAudit(self.model, obj, 'I',
                                    {}, curr_val)
                    audit_trail.create_audit()
                    return obj, created
            prev_val, curr_val = self._get_audit_values(obj, {**defaults, **kwargs})
            for k, v in six.iteritems(defaults):
                setattr(obj, k, v() if callable(v) else v)
            obj.save(using=self.db)
            audit_trail = CoreAudit(self.model, obj, 'U',
                                    prev_val, curr_val)
            audit_trail.create_audit()
        return obj, False
    
    def _get_audit_values(self, obj, data):
        prev_val = {}
        curr_val = {}
        for field, value in data.items():
            if field in [f.name for f in self.model._meta.get_fields()]:
                if obj:
                    prev_val.update({field: getattr(obj, field)})
                curr_val.update({field: value})
        return prev_val, curr_val
    
    def create(self, *args, **kwargs):
        prev_val, curr_val = self._get_audit_values(None, kwargs)
        obj = super(AuditManager, self).create(**kwargs)
        audit_trail = CoreAudit(self.model, obj, 'I',
                                prev_val, curr_val)
        audit_trail.create_audit()
        return obj


class AuditTrail(object):
    def contribute_to_class(self, cls, name):
        def connect_signals(sender, **kwargs):
            try:
                audit_ready.connect(create_model_fields, sender=AuditTrailConfig)
                pre_save.connect(pre_save_handler, sender=cls)
                post_save.connect(post_save_handler, sender=cls)
                post_delete.connect(post_delete_handler, sender=cls)
                audit_m2m_ready.connect(m2m_handler)
            except:
                pass

        def create_model_fields(sender, **kwargs):
            self.entity, created = Entity.objects.update_or_create(entity_name=cls._meta.model_name,
                                                  defaults={'primary_field':cls._meta.pk.name,
                                                            'display_format':
                                                            cls._meta.display_format})
            for field_name in cls._meta.get_fields():
                field, created = Field.objects.get_or_create(name=field_name.name,
                                                       entity=self.entity)

        def m2m_handler(sender, **kwargs):
            for field in filter(lambda x:x.many_to_many, cls._meta.local_many_to_many):
               m2m_changed.connect(m2m_signal_handler,
                                    sender=getattr(getattr(cls, field.name),
                                                   'through'))

        def pre_save_handler(sender, instance, **kwargs):
            cache_name = '{}:{}'.format(str(sender._meta.model_name), str(instance.pk))
            request = AuditMiddleware.get_request()
            if request:
                try:
                    request.session[cache_name] = sender.objects.select_related().get(pk=instance.pk)
                except ObjectDoesNotExist:
                    pass

        def post_save_handler(sender, instance, created, **kwargs):
            cache_name = '{}:{}'.format(str(sender._meta.model_name), str(instance.pk))
            request = AuditMiddleware.get_request()
            if request:
                old_instance = request.session.get(cache_name)
                prev_val = {}
                curr_val = {}
                for field in sender._meta.fields:
                    if old_instance:
                        prev_val.update({field.name: getattr(old_instance, field.name)})
                    curr_val.update({field.name: getattr(instance, field.name)})
                xaction_type = 'I' if created else 'U'
                audit = CoreAudit(sender, instance, xaction_type, prev_val, curr_val)
                audit.create_audit()
                if not created:
                    del request.session[cache_name]

        def post_delete_handler(sender, instance, *args, **kwargs):
            prev_val = {}
            curr_val = {}
            for field in sender._meta.fields:
                prev_val.update({field.name: getattr(instance, field.name)})
            xaction_type = 'D'
            audit = CoreAudit(sender, instance, xaction_type, prev_val, curr_val)
            audit.create_audit()

        def m2m_signal_handler(sender, instance, action, reverse, model, pk_set, **kwargs):
            if not reverse and (action == 'post_remove' or action ==
                                'post_add'):
                prev_val = {}
                curr_val = {}
                update_val = prev_val if action == 'post_remove' else curr_val
                for field in filter(lambda x: x.many_to_many,
                                    type(instance)._meta.get_fields()):
                    update_val.update({field.name:
                                     [v.__str__() for v in
                                      model.objects.filter(pk__in=pk_set)]})
                xaction_type = 'U'
                audit = CoreAudit(type(instance), instance, xaction_type, prev_val, curr_val)
                audit.create_m2m_audit()
        models.signals.class_prepared.connect(connect_signals, sender=cls, weak=False)


class CoreAudit(object):

    def __init__(self, audit_model, obj, xaction_type, prev_val, curr_val, *args, **kwargs):
        with transaction.atomic():
            self.audit_model = audit_model
            self.managed_fields = list(filter(lambda x: x.name in self.audit_model._meta.managed_fields, self.audit_model._meta.get_fields()) if hasattr(self.audit_model._meta, 'managed_fields') else self.audit_model._meta.get_fields())
            self.entity = Entity.objects.get(entity_name=audit_model._meta.model_name)
            self.xaction_type = xaction_type
            self.obj = obj
            self.prev_val = prev_val
            self.curr_val = curr_val
            self.request = AuditMiddleware.get_request()
            self.user = self._get_user()
            if self.user:
                self.get_diff()
                self.make_xaction()

    def valid_request(self):
        return self.request and not self.request.user.is_anonymous()
    
    def _get_user(self):
        if not self.valid_request():
            user_model = get_user_model()
            username_field = user_model.USERNAME_FIELD
            user = get_object_or_404(user_model, **{username_field:getpass.getuser()})
            return user
        return self.request.user

    def get_diff(self):
        differ = DictDiffer(self.curr_val, self.prev_val)
        self.difference = set([y for x in differ.get_diff().values() for y in x])

    def make_xaction(self):
        self.xaction = Xaction.objects.create(entity=self.entity,
                                                xaction_type=self.xaction_type,
                                              display_text=self.audit_model._meta.display_format.format(**{self.audit_model._meta.model_name:self.obj}),
                                                pfield_val=self.obj.pk,
                                                user=self.user)

    def create_audit(self):
        for field in filter(lambda x: x.name in self.difference,
                            self.managed_fields):
            self.make_field_diff(field)
        self.check_parent()

    def create_m2m_audit(self):
        for field in filter(lambda x: x.name in self.difference,
                            self.managed_fields):
            self.make_field_diff(field)
        self.check_parent()

    def make_field_diff(self, field):
        if hasattr(self.audit_model._meta, 'sensitive_fields') and field.name in self.audit_model._meta.sensitive_fields:
            self.curr_val[field.name] = self.prev_val[field.name] = '( Hidden )'
        if self.audit_model._meta.get_field(field.name).choices:
            self.curr_val[field.name] = dict(self.audit_model._meta.get_field(field.name).choices)\
                                            .get(self.curr_val[field.name])
            self.prev_val[field.name] = dict(self.audit_model._meta.get_field(field.name).choices)\
                                            .get(self.prev_val[field.name])
        content_type = field.get_internal_type().replace('Field', '')
        content_type, created = ContentType.objects.get_or_create(type=content_type)
        audit_field = Field.objects.get(entity=self.entity, name=field.name)
        curr_storage_bin = self.make_storage_bin(data=self.curr_val.get(field.name),
                                                content_type=content_type)
        prev_storage_bin = self.make_storage_bin(data=self.prev_val.get(field.name),
                                                content_type=content_type)

        FieldDiff.objects.create(xaction=self.xaction, field=audit_field,
                                        prev_val=prev_storage_bin,
                                        curr_val=curr_storage_bin)

    def make_storage_bin(self, data, content_type):
        return StorageBin.objects.create(data=str(data).encode(),
                                         content_type=content_type,
                                         status='A')

    def check_parent(self):
        if hasattr(self.audit_model._meta, 'parent_field'):
            parent_field = self.audit_model._meta.parent_field
            parent_entity = Entity.objects.get(entity_name=self.audit_model._meta.get_field(parent_field).rel.to._meta.model_name)
            child_field, created = Field.objects.get_or_create(name=parent_field,
                                                                entity=self.entity)
            parent_child_mapping, created = ParentEntityChildFieldMap.objects.get_or_create(parent_entity=parent_entity,
                                                                                            child_field=child_field)
            XactionParentEntityChildFieldMap.objects.create(xaction=self.xaction,
                                                            parent_entity_child_fields=parent_child_mapping,
                                                            field_val=self.__getattribute__(parent_field))
