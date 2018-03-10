'''
Created on 02-Feb-2017

@author: dharmikp
'''

from django.db import models

class ParentEntityChildFieldMap(models.Model):
    """
    
    """

    parent_entity = models.ForeignKey('Entity')

    child_field = models.ForeignKey('Field')

    class Meta:
        db_table = 'parent_entity_child_field_map'
