# edc-rule-groups

Write custom rules that manipulate data managed by `edc-metadata`. 

##Installation

    pip install git+https://github.com/botswana-harvard/edc-rule-groups@develop#egg=edc_rule_groups
    
add to settings:
    
    INSTALLED_APPS = [
    ...
    'edc_rule_groups.apps.AppConfig',
    ...
    ]

## Usage

For a model that use the `edc_metadata` mixin, each instance, be it the instance "to be" or the existing instance, has a corresponding metadta record. `edc_rule_groups` act on those metadata records changing the `entry_status` to either "required" or "not required".

In `edc_rule_groups` you declare a set of `Rules` contained in a `RuleGroup`. Each app has one 'rule_groups.py' that may have as many `RuleGroup` declarations as needed.

Let's start with an example from the perspective of the person entering subject data. On a dashboard there are 4 forms (models) to be completed. The "rule" is that if the subject is male, only the first two forms should be completed. If the subject is female, only the last two forms should be completed. So the metadata should show:

    Subject is Male:
    crf_one - REQUIRED, link to entry screen available
    crf_two - REQUIRED, link to entry screen available
    crf_three - NOT REQUIRED, link to entry screen not available
    crf_four - NOT REQUIRED, link to entry screen not available

    Subject is Female:
    crf_one - NOT REQUIRED
    crf_two - NOT REQUIRED
    crf_three - REQUIRED
    crf_four - REQUIRED

A `Rule` that changes the metadata if the subject is male would look like this:

    crfs_male = CrfRule(
        logic=Logic(
            predicate=P('gender', 'eq', 'MALE'),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED),
        target_models=['crfone', 'crftwo'])

The rule above has a logic attribute that evaluates like an if/else statement. If 'gender' is equal to 'MALE' then set the metadata `entry_status` for `crf_one` and `crf_two` to REQUIRED, if not, set both to NOT_REQUIRED.

### Rule Logic

The `Logic` class has a `predicate` that when evaluated is passed a few model instances each of which is checked for the `gender` attribute. If found, the predicate is evaluated to True or False.

The data that is made available for the rule `predicate` by default is:
* current visit model instance
* registered subject (see `edc_registration`)

For the rule above, `gender` would be automatically provided to the rule predicate during evaluation from registered subject.

Rules are declared as attributes of a RuleGroup much like fields in a `django` model:

    @register()
    class ExampleRuleGroup(RuleGroup):
    
        crfs_male = CrfRule(
            logic=Logic(
                predicate=P('gender', 'eq', 'MALE'),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED),
            target_models=['crfone', 'crftwo'])
    
        crfs_female = CrfRule(
            logic=Logic(
                predicate=P('gender', 'eq', FEMALE),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED),
            target_models=['crfthree', 'crffour'])
    
        class Meta:
            app_label = 'edc_example'

If the value you need for the rule `predicate` is not on either of those instances, you can pass a `source_model`. With the `source_model` declared you would have these data available:
* current visit model instance
* registered subject (see `edc_registration`)
* source model instance for the current visit
* queryset of source model for the current subject_identifier (more on this one later)

Let's say the rules changes and instead of male/female you have car/bicycle. The field for car/bicycle, `favorite_transport` is on model `CrfTransport`. The RuleGroup might look like this: 

    @register()
    class ExampleRuleGroup(RuleGroup):
    
        bicycle = CrfRule(
            logic=Logic(
                predicate=P('favorite_transport', 'eq', 'bicycle'),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED),
            target_models=['crfone', 'crftwo'])
    
        car = CrfRule(
            logic=Logic(
                predicate=P('favorite_transport', 'eq', car),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED),
            target_models=['crfthree', 'crffour'])
    
        class Meta:
            app_label = 'edc_example'
            source_model = 'CrfTransport'

#### Rule Predicates
There are two provided classes for the `predicate`, `P` and `PF`. With `P` you can make rule predicates like those above. All standard opertors can be used. For example:

    predicate = P('gender', 'eq', 'MALE')
    predicate = P('referral_datetime', 'is not', None)
    predicate = P('age', '<=', 64)

If the logic is a bit more complicated, the `PF` class allows you to pass a `lambda` function directly:

    predicate = PF('age', lambda x: True if x >= 18 and x <= 64 else False)
    
If the logic is too complicated for a simple lambda, you can just pass a function. When writing your function just remember that the `predicate` must always evaluate to True or False. 

    def my_func(visit, registered_subject, source_obj, source_qs):
        if source_obj.married and registered_subject.gender == FEMALE:
            return True
        return False

    predicate = my_func


### Rule Group Order

RuleGroups are evaluated in the order they are registered and the rules within each rule group are evaluted in the order they are declared on the RuleGroup.

### More examples

See `edc_example` for working RuleGroups and how models are configured with the `edc_metadata` mixins.
