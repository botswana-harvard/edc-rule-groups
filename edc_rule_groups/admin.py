from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from .models import RuleHistory


class EdcRuleGroupsAdminSite(AdminSite):
    site_header = 'Edc Rule Groups'
    site_title = 'Edc Rule Groups'
    index_title = 'Edc Rule Groups Administration'
    site_url = '/edc-rule-groups/'
edc_rule_groups_admin = EdcRuleGroupsAdminSite(name='edc_rule_groups_admin')


@admin.register(RuleHistory, site=edc_rule_groups_admin)
class RuleHistoryAdmin(admin.ModelAdmin):

    list_display = ('action', 'model', 'predicate', 'rule', 'timestamp')
