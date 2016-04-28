from edc_meta_data.models import CrfMetaData, CrfMetaDataHelper

from .base_rule import BaseRule


class CrfRule(BaseRule):
    """
    A CrfRule is instantiated as a class attribute of a rule group.

    * If not within a rule group, rules don't do anything...don't work;
    * The RuleGroup's Meta class determines the 'source' model and 'source_fk' model;
    * The field criteria specified in the logic refers to fields in the source model;
    * The source model has an FK attribute pointing to an instance of the source_fk
      model (with the exception of RegisteredSubject);
    * The rule specifies the target model(s) for whose meta data will be evaluated and
      possibly updated (e.g. set NEW to NOT REQUIRED);
    * Target models always have an attr pointing to an instance of the visit instance;
    * That is, Target models are scheduled models;
    * A rule changes a 'target' model's metadata entry status value.

    ..see_also:: For more about the meta data that rules operate on see module 'edc_meta_data'.

    ..see_also:: The tests also show most of the functionality of rules and rule groups.

    Usage::
        class ResourceUtilizationRuleGroup(RuleGroup):
            out_patient = CrfRule(
                logic=Logic(
                    predicate=(('out_patient', 'equals', 'no'), ('out_patient', 'equals', 'REF', 'or')),
                    consequence='not_required',
                    alternative='new'),
                target_model=['outpatientcare'])
        class Meta:
            app_label = 'bcpp_subject'
            source_fk = (SubjectVisit, 'subject_visit')
            source_model = ResourceUtilization
    """

    def __init__(self, *args, **kwargs):
        super(CrfRule, self).__init__(*args, **kwargs)
        self.entry_class = CrfMetaDataHelper
        self.meta_data_model = CrfMetaData
