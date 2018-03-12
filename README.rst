===========
Audit Trail
===========

Audit trail is a simple Django app to track the database changes in any application.


Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "audit_trail" to your INSTALLED_APPS setting like this::

       INSTALLED_APPS = [
               ...
              'audit_trail',
       ]

2. Run `python manage.py migrate` to create the audit_trail models.

3. To maintain audits of model just add an AuditTrail to that model and also add manager to it like this::

        from audit_trail.history import AuditTrail, AuditManager
        class MyModel(models.Model):
            ...

            history = AuditTrail()

            objects = AuditManager.as_manager()

            class Meta:
                display_format = '{model_name.field_name}--{model_name.another_field_name}' #You can make string format in python like this.

4. To add admin screen for audit simply inherit AuditTrailLogAdmin in your model admin like below::
   
        from audit_trail.admin import AuditTrailLogAdmin
        class MyModelAdmin(AuditTrailLogAdmin):
            ...

   Visit django model admin screen to get the history of particular
   model(Click on History button in that screen).

5. To get audit trail of many_to_many fields just send signal from your AppConfig class' ready method like this::
        
        from audit_trail.signals import audit_m2m_ready

        class MyappConfig(AppConfig):
            ...
            def ready(self):
                audit_m2m.ready.send(sender=self.__class__)
                ...

6. To get audit trail logs in your django app import and call function
   get_history_list() like this::

        from audit_trail.admin import get_history_list
        get_history_list(model_name, object_id)

