'''
Created on 06-Jan-2017

@author: dharmikp
'''
from django.db import models
from django.utils.translation import ugettext_lazy as _

from audit_trail.choices import status_choices

class Entity(models.Model):
    """
    Entity model for the History.
    """

    entity_name = models.CharField(_('Email Address'), max_length=64, null=False,
                                   blank=False, unique=True)
    """
    Name of the entity.
    """

    primary_field = models.CharField(_('Primary Field'), max_length=64, null=False,
                                       blank=False)
    """
    Primary key field of that particular entity.
    """

    display_format = models.CharField(_('Display Format'), max_length=255, null=True,
                                      blank=True)
    """
    Display format for the value of the entity.
    """

    status = models.CharField(_('Status'), max_length=1, default='A',
                                null=False, db_column='status', blank=False,
                                choices=status_choices)
    """
    Status of the Entity. Maximum 1 Character allowed in this field and it can not be null
    It can have two values A:Active, I:Inactive.
    """

    class Meta:
        db_table = 'entity'
        verbose_name_plural = _('Entities')
        verbose_name = _('Entity')

