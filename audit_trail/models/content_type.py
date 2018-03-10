'''
Created on 09-Jan-2017

@author: dharmikp
'''
from django.db import models
from django.utils.translation import ugettext_lazy as _

class ContentType(models.Model):
    """
    Content type of the data.
    """

    type = models.CharField(_('Type'), max_length=64, null=False, blank=False,
                            unique=True)
    """
    Name of content Type.
    """

    class Meta:
        db_table = 'content_type'
        verbose_name_plural = _('Content Types')
        verbose_name = _('Content type')

    def __str__(self):
        return self.type
