Rule Groups
===========

Note that fields from RegisteredSubject, like gender, can be used. The :class:`ScheduledDataRule` class 
will catch the field name in the predicate and substitute the value from RegisteredSubject 
for the current subject.

.. code-block:: python
    
    from bhp_entry_rules.classes import RuleGroup, ScheduledDataRule, Logic, rule_groups
    from mochudi_subject.models import SubjectVisit, Qn002
    
    
    class Qn002RuleGroup(RuleGroup):
    
        sex_had_interc = ScheduledDataRule(
            logic=Logic(
                predicate=('sex_had_interc', 'equals', 'yes'),
                consequence='new',
                alternative='not_required'),
            target_model=['qn002sectioneightintro', 
                          'qn002sectioneightpartnerrecent', 
                          'qn002sectioneightpartnersecond', 
                          'qn002sectioneightpartnerthird'])
    
        is_tested_hiv = ScheduledDataRule(
            logic=Logic(
                predicate=('is_tested_hiv', 'equals', 'yes'),
                consequence='new',
                alternative='not_required'),
            target_model=['qn002sectionseven'])
    
        gender = ScheduledDataRule(
            logic=Logic(
                predicate=('gender', 'equals', 'm'),
                consequence='new',
                alternative='not_required'),
            target_model=['qn002sectionfour', 'qn002sectionfive'])
    
        gender = ScheduledDataRule(
            logic=Logic(
                predicate=('gender', 'equals', 'f'),
                consequence='new',
                alternative='not_required'),
            target_model=['qn002sectionfsix'])
    
        class Meta:
            app_label = 'mochudi_subject'
            filter_model = (SubjectVisit, 'subject_visit')
            source_model = Qn002
    rule_groups.register(Qn002RuleGroup)
