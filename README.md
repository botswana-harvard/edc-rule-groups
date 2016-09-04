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

place a `rule_groups.py` in the app root with your rule groups.

On bootup see the file was found and loaded:

    Loading Edc Rule Groups ...
     * checking for rule_groups ...
     * registered rule groups from application 'edc_example'
     Done loading Edc Rule Groups.

Inspect rule groups from the site registry:

    >>> from edc_rule_groups.site_rule_groups import site_rule_groups
        
    >>> for rule_groups in site_rule_groups.registry.values():
    >>>    for rule_group in rule_groups:
    >>>        print(rule_group._meta.rules)
    
    (<edc_example.rule_groups.ExampleRuleGroup: crfs_male>, <edc_example.rule_groups.ExampleRuleGroup: crfs_female>)
    (<edc_example.rule_groups.ExampleRuleGroup2: bicycle>, <edc_example.rule_groups.ExampleRuleGroup2: car>)    
    
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

The `Logic` class has a rule `predicate` that when evaluated is passed a few model instances each of which is checked for the `gender` attribute. If found, the predicate is evaluated to True or False.

The data that is made available for the rule `predicate` by default is:
* current visit model instance
* registered subject (see `edc_registration`)

For the rule above, `gender` would be automatically provided to the rule predicate during evaluation from registered subject.

### Rule Groups

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

Rule group class declarations are placed in file `rule_groups.py` in the root of your application. They are registered in the order in which they appear in the file. All rule groups are available from the `site_rule_groups` global.

### More on Rule Logic and Rule Predicates

#### Logic

The `consequence` and `alternative` except these values:
    
    from edc_metadata.constants import REQUIRED, NOT_REQUIRED
    from edc_rule_groups.constants import DO_NOTHING

    * REQUIRED
    * NOT_REQUIRED
    * DO_NOTHING 

It is recommended to write the logic so that if the `predicate` evaluated to  `True`, the `consequence` is REQUIRED.

#### Rule Predicate values

In the examples above, the rule `predicate` can only access values that can be found on the subjects's current `visit` instance or `registered_subject` instance. If the value you need for the rule `predicate` is not on either of those instances, you can pass a `source_model`. With the `source_model` declared you would have these data available:

* current visit model instance
* registered subject (see `edc_registration`)
* source model instance for the current visit
* queryset of source model for the current subject_identifier (more on this one later)

Let's say the rules changes and instead of refering to `gender` (male/female) you wish to refer to the value field of `favorite_transport` on model `CrfTransport`. `favorite_transport` can be "car" or "bicycle". You want the first rule `predicate` to read as:

* "If `favorite_transport` is equal to `bicycle` then set the metadata `entry_status` for `crf_one` and `crf_two` to REQUIRED, if not, set both to NOT_REQUIRED" 

and the second to read as:

* "If `favorite_transport` is equal to `car` then set the metadata `entry_status` for `crf_three` and `crf_four` to REQUIRED, if not, set both to NOT_REQUIRED".

The field for car/bicycle, `favorite_transport` is on model `CrfTransport`. The RuleGroup might look like this: 

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

Note that `CrfTransport` is a `crf` model in the Edc. That is, it has a `foreign key` to the visit model. Internally the query will be constructed like this:
    
    # source model instance for the current visit 
    visit_attr = 'subject_visit'
    source_obj = CrfTansport.objects.get(**{visit_attr: visit}) 
    
    # queryset of source model for the current subject_identifier
    visit_attr = 'subject_visit'
    source_qs = CrfTansport.objects.filter(**{'{}__subject_identifier'.format(visit_attr): subject_identifier}) 
    

#### More Complex Rule Predicates

There are two provided classes for the rule `predicate`, `P` and `PF`. With `P` you can make simple rule predicates like those used in the examples above. All standard opertors can be used. For example:

    predicate = P('gender', 'eq', 'MALE')
    predicate = P('referral_datetime', 'is not', None)
    predicate = P('age', '<=', 64)

If the logic needs to a bit more complicated, the `PF` class allows you to pass a `lambda` function directly:

    predicate = PF('age', lambda x: True if x >= 18 and x <= 64 else False)
    
If the logic needs to be more complicated than is recommended for a simple lambda, you can just pass a function. When writing your function just remember that the rule `predicate` must always evaluate to True or False. 

    def my_func(visit, registered_subject, source_obj, source_qs):
        if source_obj.married and registered_subject.gender == FEMALE:
            return True
        return False

    predicate = my_func


### Rule Group Order

RuleGroups are evaluated in the order they are registered and the rules within each rule group are evaluated in the order they are declared on the RuleGroup.


### Testing

Since the order in which rules run matters, it is essential to test the rules together. See `tests` for some examples. When writing tests it may be helpful to know the following:

* the standard Edc model configuration assumes you have consent->enrollment->appointments->visit->crfs and requisitions. 
* rules can be instected after boot up in the global registry `site_rule_groups`.
* all rules are run when the visit  

### More examples

See `edc_example` for working RuleGroups and how models are configured with the `edc_metadata` mixins. The `tests` in `edc_rule_groups` use the rule group and model classes in `edc_example`. 


### Notes on Edc 

The standard Edc model configuration assumes you have a data entry flow like this:

    consent->enrollment->appointment->visit (1000)->crfs and requisitions
                         appointment->visit (2000)->crfs and requisitions
                         appointment->visit (3000)->crfs and requisitions
                         appointment->visit (4000)->crfs and requisitions
                         ...
(You should also see the other dependencies, `edc_consent`, `edc_visit_schedule`, `edc_appointment`, `edc_visit_tracking`, `edc_metadata`, etc.)

### Signals

In the `signals` file: 

visit model `post_save`:

* Metadata is created for a particular visit and visit code, e.g. 1000, when the `visit` model is saved for a subject and visit code using the default `entry_status` configured in the `visit_schedule`.
* Immediately after creating metadata, all rules for the `app_label` are run in order. The `app_label` is the `app_label` of the visit model.

crf or requisition model `post_save`:

* the metadata instance for the crf/requisition is updated and then all rules are run.

crf or requisition model `post_delete`:

* the metadata instance for the crf/requisition is reset to the default `entry_status` and then all rules are run.
