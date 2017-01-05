import sys

from django.apps import AppConfig as DjangoAppConfig

from edc_rule_groups.site_rule_groups import site_rule_groups
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_rule_groups'
    verbose_name = 'Edc Rule Groups'

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_rule_groups.autodiscover()
        if not site_rule_groups.registry:
            sys.stdout.write(style.ERROR(
                ' Warning. No rule groups have loaded.\n'.format(self.verbose_name)))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
