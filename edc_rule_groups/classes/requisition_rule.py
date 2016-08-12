try:
   from django.db import models as apps
except:
   from django.apps import apps

from edc_base.utils import convert_from_camel
from edc_meta_data.models import RequisitionMetaData, RequisitionMetaDataHelper

from .base_rule import BaseRule


class RequisitionRule(BaseRule):
    """A RequisitionRule is instantiated as a class attribute of a rule group."""

    def __init__(self, *args, **kwargs):
        self.target_requisition_panel = None
        super(RequisitionRule, self).__init__(*args, **kwargs)
        if 'target_requisition_panels' not in kwargs:
            raise KeyError('{0} is missing required attribute \'target_requisition_panels\''.format(
                self.__class__.__name__))
        self.entry_class = RequisitionMetaDataHelper
        self.meta_data_model = RequisitionMetaData
        self.target_requisition_panels = kwargs.get('target_requisition_panels')

    def run(self, visit_instance):
        """ Evaluate the rule for the requisition model for each requisition panel."""
        for target_model in self.target_model_list:  # is a requisition model(s)
            for self.target_requisition_panel in self.target_requisition_panels:
                self.visit_instance = visit_instance
                self.target_model = target_model
                self.registered_subject = self.visit_instance.appointment.registered_subject
                self.visit_attr_name = convert_from_camel(self.visit_instance._meta.object_name)
                self._source_instance = None
                self._target_instance = None
                change_type = self.evaluate()
                if change_type and self.target_model:
                    self.target_model.entry_meta_data_manager.visit_instance = self.visit_instance
                    self.target_model.entry_meta_data_manager.target_requisition_panel = self.target_requisition_panel
                    try:
                        self.target_model.entry_meta_data_manager.instance = self.target_model.objects.get(
                            **self.target_model.entry_meta_data_manager.query_options)
                    except self.target_model.DoesNotExist:
                        self.target_model.entry_meta_data_manager.instance = None
                    self.target_model.entry_meta_data_manager.update_meta_data_from_rule(change_type)

    @property
    def target_model(self):
        return self._target_model

    @target_model.setter
    def target_model(self, model_cls):
        """Sets the target models to a model class from the target_model_list or None.

        Target models are the models for whose meta data is affected by the rule.

        Target models always have an attribute pointing to the visit instance.

        Target models must be listed in the visit definition for the
        current visit_instance, e.g. Entry of visit_instance.appointment.visit_definition.
        If it is not listed in the visit_definition, target_model returns None."""

        self._target_model = None
        try:
            model_cls = apps.get_model(self.app_label, model_cls)
        except AttributeError:
            pass
        try:
            self.entry_class.entry_model.objects.get(
                visit_definition=self.visit_instance.appointment.visit_definition,
                requisition_panel__name=self.target_requisition_panel,
                app_label=model_cls._meta.app_label,
                model_name=model_cls._meta.object_name.lower())
            self._target_model = model_cls
        except self.entry_class.entry_model.DoesNotExist:
            pass
