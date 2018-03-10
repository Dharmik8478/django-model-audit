'''
Created on 02-Fab-2017

@author: dharmikp
'''

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from audit_trail.choices import xaction_type_choice


class Xaction(models.Model):
    """
    Transaction table for maintaining transaction of audit trail.
    """

    id = models.BigAutoField(primary_key=True)
    """
    Id field of xaction, it is auto increment.
    """

    entity = models.ForeignKey('Entity', verbose_name='Entity',
                               related_name='xactions')
    """
    Foreign key to entity.
    """

    xaction_type = models.CharField(_('Xaction Type'), max_length=1,
                                    choices=xaction_type_choice, null=False,
                                    blank=False)
    """
    Type of the transaction.
    """

    display_text = models.CharField(_('Display Text'), max_length=128, null=True,
                                    blank=True)
    """
    Display text for the transaction.
    """

    pfield_val = models.CharField(_('Primary Field Value'), max_length=128,
                                  null=False, blank=False)
    """
    Primary field value of the transaction object.
    """

    ts = models.DateTimeField(_('Time Stamp'), null=False, blank=False,
                                      auto_now_add=True)
    """
    Time stamp when this transaction is happen.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='User')
    """
    Foreign key to the user model.
    """

    class Meta:
        db_table = 'xaction'
        verbose_name_plural = _('Xactions')
        verbose_name = _('Xaction')
        ordering =['-ts']

