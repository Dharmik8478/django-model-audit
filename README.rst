===========
Audit Trail
===========

Audit trail is a simple Django app to track the database changes and maintain history in any application. It also provide history for many_to_many fields, with ready admin page.


Quick start
-----------
1. Install django-model-audit::

       pip install django-model-audit

2. Add "audit_trail" to your INSTALLED_APPS::

       INSTALLED_APPS = [
               ...
              'audit_trail',
       ]

3. Add Middlewre::
       
       MIDDLEWARE = [
              ...
              'audit_trail.middleware.AuditMiddleware'
       ]

4. Run Migrate::

       python manage.py migrate

5. Add an AuditTrail and manager to model you want to create history::

        from audit_trail.history import AuditTrail, AuditManager
        class MyModel(models.Model):
            ...

            history = AuditTrail()

            objects = AuditManager.as_manager()

            class Meta:
                display_format = '{model_name.field_name}'

6. To add admin screen for audit simply inherit AuditTrailAdmin in your model admin::
   
        from audit_trail.admin import AuditTrailAdmin
        class MyModelAdmin(AuditTrailAdmin):
            ...

   Visit django model admin screen to get the history of particular
   model(Click on History button in that screen).

7. To get audit trail of many_to_many fields just send signal from your AppConfig class' ready method::
        
        from audit_trail.signals import audit_m2m_ready

        class MyappConfig(AppConfig):
            ...
            def ready(self):
                audit_m2m.ready.send(sender=self.__class__)
                ...

8. To get audit trail logs in your django app import and call function
   get_audit_trail() like this::

        from audit_trail.admin import get_audit_trail
        get_audit_trail(model_name, object_id)

