import sys

from django.apps import AppConfig as DjangoAppConfig

from edc_rule_groups.site_rule_groups import site_rule_groups


class AppConfig(DjangoAppConfig):
    name = 'edc_rule_groups'
    verbose_name = 'Edc Rule Groups'

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_rule_groups.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
