'''
Created on 02-Feb-2017

@author: dharmikp
'''
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Field(models.Model):
    """
    Class for storing fields of entity.
    """

    name = models.CharField(_('Name'), max_length=80,
                            null=False, blank=False)
    """
    Name of the field.
    """

    entity = models.ForeignKey('Entity', verbose_name='Entity',
                               related_name='fields')
    """
    Foreign key to entity.
    """

    class Meta:
        db_table = 'field'
        verbose_name_plural = _('Fields')
        verbose_name = _('Field')
        unique_together = ('name', 'entity')

