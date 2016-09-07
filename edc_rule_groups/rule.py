from django.apps import apps as django_apps

from .constants import DO_NOTHING


class Rule:

    def __init__(self, logic):

        self.source_model = None  # set by metaclass
        # self.source_fk_model = None  # set by metaclass
        # self.source_fk_attr = None  # set by metaclass
        self.name = None  # set by metaclass
        self.group = None  # set by metaclass
        self.app_label = None  # set by metaclass
        self.logic = logic

    def __repr__(self):
        return '<{}.rule_groups.{}: {}>'.format(self.app_label, self.group, self.name)

    def run(self, visit):
        """ Runs the rule for each model in target_models and updates metadata if the model
        instance does not exist."""
        try:
            app_config = django_apps.get_app_config('edc_registration')
            registered_subject = app_config.model.objects.get(subject_identifier=visit.subject_identifier)
        except app_config.model.DoesNotExist:
            registered_subject = None
        if self.source_model:
            source_model = django_apps.get_model(*self.source_model)
            try:
                source_obj = source_model.objects.get_for_visit(visit)
            except source_model.DoesNotExist:
                source_obj = None
            source_qs = source_model.objects.get_for_subject_identifier(visit.subject_identifier)
        else:
            source_obj = None
            source_qs = None
        for target_model in self.target_models:
            target_model = django_apps.get_model(*target_model.split('.'))
            if self.runif:
                if self.source_model and not source_obj:
                    pass  # without source_obj, predicate will fail
                else:
                    self.run_rules(target_model, visit, registered_subject, source_obj, source_qs)

    def run_rules(self, target_model, visit, *args):
        try:
            target_model.objects.get_for_visit(visit)
        except target_model.DoesNotExist:
            entry_status = self.evaluate(visit, *args)
            visit.metadata_update_for_model(
                target_model._meta.label_lower,
                entry_status=entry_status)

    @property
    def runif(self):
        """May be overridden to run only on a condition."""
        return True

    def evaluate(self, visit, *args):
        """ Evaluates the predicate function and returns a result."""
        if self.logic.predicate(visit, *args):
            result = self.logic.consequence if self.logic.consequence != DO_NOTHING else None
        else:
            result = self.logic.alternative if self.logic.alternative != DO_NOTHING else None
        return result

    @property
    def __doc__(self):
        return self.logic.predicate.__doc__ or "missing docstring for {}".format(self.logic.predicate)
