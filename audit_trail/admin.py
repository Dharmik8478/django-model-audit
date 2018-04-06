from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.db.models.expressions import F
from django.contrib.admin.utils import unquote
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string


class AuditTrailAdmin(admin.ModelAdmin):
    
    def audit_col(self, obj):
        opts =  self.model._meta
        app_label = opts.app_label
        model_name = opts.model_name
        history_url = reverse('admin:'+app_label+'_'+model_name+'_history', args=(obj.id,))
        return render_to_string('audit_trail/admin_cl_icon.html', {'history_url': history_url})
    
    audit_col.allow_tags = True
    audit_col.short_description = _('History')
    
    def history_view(self, request, object_id, extra_context=None):
        model = self.model

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        opts =  model._meta
        app_label = opts.app_label
        action_list = get_audit_trail(model._meta.model_name, object_id)

        context = dict(
            self.admin_site.each_context(request),
            title=_('History: %s' % force_text(obj)),
            action_list=action_list,
            module_name=capfirst(force_text(opts.verbose_name_plural)),
            object=obj,
            opts=opts,
            preserved_filters=self.get_preserved_filters(request),
        )
        context.update(extra_context or {})

        request.current_app = self.admin_site.name

        return TemplateResponse(request, 'audit_trail/history.html', context)


def get_audit_trail(model_name, object_id):
    FieldDiff = apps.get_model('audit_trail', 'FieldDiff')
    return FieldDiff.objects.filter((Q(xaction__entity__entity_name=model_name, xaction__pfield_val=object_id)
                    | Q(xaction__xaction_parent_entity_child_fields__parent_entity_child_fields__parent_entity__entity_name=model_name,
                        xaction__xaction_parent_entity_child_fields__field_val=object_id))).\
                    order_by('-xaction__ts').\
                    annotate(transacted_on=F('xaction__ts'),
                                transacted_by=F('xaction__user__'+get_user_model().USERNAME_FIELD),
                                transaction_type=F('xaction__xaction_type'),
                                field_name=F('field_id__name'),
                                current_val=F('curr_val__data'),
                                current_val_type=F('curr_val__content_type__type'),
                                previous_val=F('prev_val__data'),
                                previous_val_type=F('prev_val__content_type__type')
				).\
                    values('transacted_on',
                           'transacted_by',
                           'transaction_type',
                           'field_name',
                           'current_val',
                           'current_val_type',
                           'previous_val',
                           'previous_val_type',
                           'xaction__display_text'
                          )

