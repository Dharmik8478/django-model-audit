'''
Created on 19-Jan-2017

@author: dharmikp
'''
from django.db import models

class XactionParentEntityChildFieldMap(models.Model):
    """
    Mapping table for xaction and parent Entity to Child Field.
    """

    xaction = models.ForeignKey('Xaction', related_name='xaction_parent_entity_child_fields')
    """
    Foreign key to xaction model.
    """

    parent_entity_child_fields = models.ForeignKey('ParentEntityChildFieldMap')
    """
    Foreign key to parent entity child field mapping table.
    """

    field_val = models.CharField(max_length=128)
    """
    Value of primary key of parent entity in string form.
    """

    class Meta:
        db_table = 'xaction_parent_entity_child_field_map'
