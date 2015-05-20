import copy

from collections import OrderedDict

from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from edc.subject.entry.models import Entry

from edc_rule_groups import RuleGroup


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Controller(object):

    """ Main controller of :class:`RuleGroup` objects. """

    def __init__(self):
        self._registry = OrderedDict()  # ordered to ensure rules fire in the same order as listed in the source module.

    def set_registry(self, rule_group):
        if not issubclass(rule_group, RuleGroup):
            raise AlreadyRegistered('Expected an instance of RuleGroup.')
        if rule_group.app_label not in self._registry:
            self._registry.update({rule_group.app_label: []})
        if rule_group in self._registry.get(rule_group.app_label):
            raise AlreadyRegistered('The rule {0} is already registered for module {1}'.format(rule_group.__name__, rule_group.app_label))
        self._registry.get(rule_group.app_label).append(rule_group)

    def get_registry(self, app_label=None):
        """Returns the an ordered dictionary of rules for the app_label."""
        if app_label:
            if app_label in self._registry:
                return self._registry.get(app_label)
            else:
                return {}
        return self._registry

    def register(self, rule_group):
        """ Register Rule groups to the list for the module the rule groups were declared in; which is the same module as the visit model (see update)."""
        self.set_registry(rule_group)

    def unregister(self, rule_group):
        self._registry[rule_group.app_label].pop(self._registry[rule_group.app_label].index(rule_group))

    def update_all(self, visit_model_instance):
        """Given a visit model instance, run all rules in each rule group for the app_label of the visit model."""
        app_label = visit_model_instance._meta.app_label
        for rule_group in self.get_registry(app_label):
            for rule in rule_group.rules:
                rule.run(visit_model_instance)

    def update_for_visit_definition(self, visit_instance):
        """Given a visit model instance, run all rules in the rule group module for the visit definition in order of the entries (rule source model)."""
        for entry in Entry.objects.filter(visit_definition__code=visit_instance.appointment.visit_definition.code).order_by('entry_order'):
            source_model = entry.get_model()
            for rule in self.get_rules_for_source_model(source_model, visit_instance._meta.app_label):
                rule.run(visit_instance)

    def update_rules_for_source_model(self, source_model, visit_instance):
        """Runs all rules that have a reference to the given source model (rule.source_model)."""
        for rule in self.get_rules_for_source_model(source_model, visit_instance._meta.app_label):
            rule.run(visit_instance)

    def update_rules_for_source_fk_model(self, source_fk_model, visit_instance):
        """Runs all rules that have a reference to the given source FK model (rule.source_fk_model)."""
        for rule in self.get_rules_for_source_fk_model(source_fk_model, visit_instance._meta.app_label):
            rule.run(visit_instance)

    def get_rules_for_source_model(self, source_model, app_label):
        """Returns a list of rules for the given source_model."""
        rules = []
        for rule_group in self.get_registry(app_label):
            for rule in rule_group.rules:
                if rule.source_model == source_model:
                    if rule.runif:
                        rules.append(rule)
        return rules

    def get_rules_for_registered_subject(self, app_label):
        """Returns a list of rules for the given source_fk_model."""
        rules = []
        for rule_group in self.get_registry(app_label):
            for rule in rule_group.rules:
                if rule.source_model._meta.object_name.lower() == 'registeredsubject':
                    rules.append(rule)
        return rules

    def get_rules_for_source_fk_model(self, source_fk_model, app_label):
        """Returns a list of rules for the given source_fk_model."""
        rules = []
        for rule_group in self.get_registry(app_label):
            for rule in rule_group.rules:
                if rule.source_fk_model == source_fk_model:
                    rules.append(rule)
        return rules

    def autodiscover(self):
        """ Autodiscover rules from a edc_rule_groups module."""
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try:
                before_import_registry = copy.copy(site_rule_groups._registry)
                import_module('%s.edc_rule_groups' % app)
            except:
                site_rule_groups._registry = before_import_registry
                if module_has_submodule(mod, 'edc_rule_groups'):
                    raise

site_rule_groups = Controller()
