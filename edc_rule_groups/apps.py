from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_rule_groups'
    verbose_name = 'Edc Rule Groups'
