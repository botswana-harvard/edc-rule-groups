Building Model Rules
====================

Rules are attributes of a RuleGroup
-------------------------------------

The rules are added as attributes to a subclass of :class:`~bhp_entry_rules.classes.rule_group.RuleGroup` like this::
    
    class HivHistoryRuleGroup(RuleGroup):
    
        rule = ....
        
        rule = ....
        
        class Meta:
            app_label = ....
            filter_model = ....
            source_model = ...       

RuleGroups are declared in a module or :file:`rule_groups.py` 
-------------------------------------------------------------

RuleGroups are declared in :file:`rule_groups.py`. Place the file in the root of your app. 


By Default, Rules Evaluate When the Dashboard is refreshed
-----------------------------------------------------------

The rules in a class evaluate when the dashboard is refreshed. 

Rules Evaluate in Order
-----------------------

Rules evaluate in the order in which they appear in the :file:`rule_groups.py`. 
Design and order your rules knowing 
that the action of a rule can be undone by that of a rule that follows later in the file.

Rules can access fields in RegisteredSubject 
--------------------------------------------

If a predicate refers to a field name that appears in RegisteredSubject, it will be 
evaluated using the RegisteredSubject model and not the source model. Default field names are not included, 
such as, id, hostname_created, modified, user_created, etc.

In the example below, 
    * the rule is built with :class:`AdditionalDataRule` which when evalutated as 'required' will
      add a required form to the dashboard visible at any visit (PRN form).
    * the field 'sid' will be evaluated against an instance of RegisteredSubject for this infant;
    * the predicate has two tuples which evaluate to a predicate with two logic
      phrases joined by 'and';
    * the second tuple compares 'sid' to None
    * the second tuple has 4 items, where the last item is the logic operator for the two
      phrases in the evaluated predicate.
       
.. code-block:: python

    class InfantPrerandoLossRuleGroup(RuleGroup):
    
        lost = AdditionalDataRule(
            logic=Logic(
                predicate=(('reason', 'equals', 'lost'), ('sid', 'equals', None, 'and')),
                consequence='required',
                alternative='not_required'),
            target_model=['infantprerandoloss', 'infantoffstudy'])
    
        class Meta:
            app_label = 'mpepu_infant'
            source_model = InfantVisit
            filter_model = (RegisteredSubject, 'registered_subject')
    rule_groups.register(InfantPrerandoLossRuleGroup)
    
    
    class InfantPrerandoLossOffDrugRuleGroup(RuleGroup):
    
        lost_off_drug = AdditionalDataRule(
            logic=Logic(
                predicate=(('reason', 'equals', 'lost'), ('sid', 'ne', None, 'and')),
                consequence='required',
                alternative='not_required'),
            target_model=['infantoffdrug', 'infantoffstudy'])
    
        class Meta:
            app_label = 'mpepu_infant'
            source_model = InfantVisit
            filter_model = (RegisteredSubject, 'registered_subject')
    rule_groups.register(InfantPrerandoLossOffDrugRuleGroup)