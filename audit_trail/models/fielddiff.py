'''
Created on 06-Jan-2017

@author: dharmikp
'''

from django.db import models
from django.utils.translation import ugettext_lazy as _


class FieldDiff(models.Model):
    """
    Difference between fields.
    """

    id = models.BigAutoField(primary_key=True)
    """
    Id field of field diff, it is auto increment.
    """

    xaction = models.ForeignKey('Xaction', verbose_name='Xaction')
    """
    Foreign key to Xaction model.
    """

    field = models.ForeignKey('Field', verbose_name='Field')
    """
    Foreign key to Firld model.
    """

    prev_val = models.ForeignKey('StorageBin', verbose_name='Previous Value',
                                 related_name='prev_field_diff')
    """
    Foreign key to storage bin model for previous value.
    """

    curr_val = models.ForeignKey('StorageBin', verbose_name='Current Value',
                                 related_name='curr_field_diff')
    """
    Foreign key to storage bin model for current value.
    """

    class Meta:
        db_table = 'fielddiff'
        verbose_name_plural = _('Field Diffs')
        verbose_name = _('Field Diff')

