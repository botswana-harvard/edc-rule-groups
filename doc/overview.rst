Overview
========

Module bhp_entry_rules allows you to build logic into a subject's dashboard that manipulates
which forms are required and which are not. By default, all forms on a dashboard
are required. 

If, for example, your visit definition presents 6 forms to be completed at a visit, 
of which two are not required if the subject is HIV Negative, a rule could be defined to 
handle this. Your rule logic can source information from other forms 
and data.

Additional forms not scheduled within a visit, such as an Off-Study form or Death form can also, through your logic, 
be presented to the user for completion.

Rules are grouped into "rule groups" and stored in a single module in your app. The module must be named "rule_groups".

Let's start with an example:

.. code-block:: python

    class MaternalHivRuleGroup(RuleGroup):
    
        pos = ScheduledDataRule(
            logic=Logic(
                predicate=('hiv_status', 'equals', 'pos'),
                consequence='new',
                alternative='not_required'),
            target_model=['hivstatuspos'])
    
        neg = ScheduledDataRule(
            logic=Logic(
                predicate=('hiv_status', 'equals', 'neg'),
                consequence='new',
                alternative='not_required'),
            target_model=['hivstatusneg', 'newhaart'])
    
        class Meta:
            app_label = 'maikalelo_maternal'
            filter_model = (MaternalVisit, 'maternal_visit')
            source_model = RegisteredSubject
    rule_groups.register(MaternalHivRuleGroup)

In this example, the rule group :class:`MaternalHivRuleGroup` contains two rules: "pos" and "neg". 
Both are instances of :class:`ScheduledDataRule`. The rule needs to understand your logic and which models to "target". 
Your logic is an IF-THEN-ELSE construct where the "predicate" is a tuple that will be resolved into
"hiv_status == 'pos'". If True, the target model :class:`HivStatusPos` will be flagged as "New", if False, as "Not Required".
Attribute 'target model' is a list and as with the second rule, 'neg', can include more than one model name. 

The predicate tuple refers to 'hiv_status'. This is a field attribute and, in this case, is an attribute of the :class:`RegisteredSubject` 
as defined in the class Meta attribute 'source_model'. The source model can be defined in Meta, as in this example, or as an
attribute of the rule. If you define both, the source_model defined in the rule will prevail. Either way, the field in the
predicate must be an attribute of the source model and the source_model must be defined.

Lastly, the RuleGroup needs to know how to filter your source model to get the instance for the current visit that your dashboard is focused
on. For this you provide the app_label and filter_model. The filter model is a tuple of ModelClass and the foreign key in your source model
for this ModelClass.

You may know that model RegisteredSubject does not have a key to a visit model. :mod:`bhp_registration.model.RegisteredSubject` is heavily used by the
EDC and has some useful demographic data useful for rules. The rule class actually gets the RegisteredSubject instance from the visit model. 
Anyway, using RegisteredSubject as a source model is a special case. But if the HIV status was asked in a 
scheduled model for the current visit, the filter model tuple would help to get the correct instance
of that scheduled source model.

A few points:
    * The visit model is always passed to the rule;
    * In most cases the filter model and the visit model are the same, but they do not have to be;
    * If the source model instance does not exist, the rule does not run;
    * Rules run in the order that they appear in the RuleGroup;
    * RulesGroups are evaluated in the order that they appear in the rule_groups module.
