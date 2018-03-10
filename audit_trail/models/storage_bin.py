'''
Created on 02-Feb-2017

@author: dharmikp
'''
import base64
import random
import string

from audit_trail.choices import status_choices
from django.db import models
from django.utils.translation import ugettext_lazy as _


class StorageBin(models.Model):
    """
    Actual storage for the Audit trail module.
    """

    id = models.BigAutoField(primary_key=True)
    """
    Id field of storage bin, it is auto increment.
    """

    stored_at = models.DateTimeField(_('Stored At'), null=False, blank=False,
                                      auto_now_add=True)
    """
    Time stamp of storing data.
    """

    code = models.CharField(_('Code'), max_length=16, unique=True, null=False,
                            blank=False,)
    """
    A random string made from upper case English alphabets and digits 0 to 9
    which should be used to search for this record, wherever applicable.
    """

    content_type = models.ForeignKey('ContentType', verbose_name='Content Type')
    """
    Boolean field of the Field showing whether field is collection or not.
    """

    data = models.BinaryField() 

    """
    Data to store.
    """

    status = models.CharField(_('Status'), max_length=1, default='A',
		              null=False, db_column='status', blank=False,
                              choices=status_choices)
    """
    Status of the Storage bin. Maximum 1 Character allowed in this field and it can not be null
    It can have two values A:Active, I:Inactive.
    """
    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        super(StorageBin, self).save(*args, **kwargs)

    class Meta:
        db_table = 'storage_bin'
        verbose_name_plural = _('Storage Bins')
        verbose_name = _('Storage Bin')

