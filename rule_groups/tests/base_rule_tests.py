from django.test import TestCase

from edc.constants import NOT_REQUIRED, NEW
from edc.core.bhp_variables.models import StudySite
from edc.entry_meta_data.models import ScheduledEntryMetaData
from edc.lab.lab_profile.classes import site_lab_profiles
from edc.lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc.subject.appointment.models import Appointment
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc.subject.registration.models import RegisteredSubject
from edc.subject.rule_groups.classes import site_rule_groups
from edc.subject.visit_schedule.models import VisitDefinition
from edc.testing.classes import TestLabProfile
from edc.testing.classes import TestVisitSchedule, TestAppConfiguration
from edc.testing.models import TestVisit, TestScheduledModel1, TestScheduledModel2, TestConsentWithMixin
from edc.testing.tests.factories import TestConsentWithMixinFactory, TestScheduledModel1Factory, TestVisitFactory

from ..classes import RuleGroup, BaseRule, ScheduledDataRule, Logic
from edc.subject.visit_tracking.models import BaseVisitTracking


def func_condition_true(visit_instance):
    if not isinstance(visit_instance, BaseVisitTracking):
        raise TypeError('func didnt get a visit instance')
    if visit_instance:
        name = 'Erik'
    return name == 'Erik'


def func_condition_false(visit_instance):
    if not isinstance(visit_instance, BaseVisitTracking):
        raise TypeError('func didnt get a visit instance')
    if visit_instance:
        name = 'Erik'
    return name == 'Bob'


class RuleTests(TestCase):

    app_label = 'testing'
    consent_catalogue_name = 'v1'

    def setUp(self):

        try:
            site_lab_profiles.register(TestLabProfile())
        except AlreadyRegisteredLabProfile:
            pass
        TestAppConfiguration()
        site_lab_tracker.autodiscover()
        TestVisitSchedule().build()

        # a test rule group where the source model is RegisteredSubject
        # the rules in this rule group will be only evaluated when the visit instance
        # is created or saved. Note source_fk is None.
        class TestRuleGroupRs(RuleGroup):
            test_rule = ScheduledDataRule(
                logic=Logic(
                    predicate=(('gender', 'equals', 'M')),
                    consequence='not_required',
                    alternative='new'),
                target_model=['testscheduledmodel1'])

            class Meta:
                app_label = 'testing'
                source_fk = None
                source_model = RegisteredSubject
        site_rule_groups.register(TestRuleGroupRs)

        # a test rule group where the source model is a scheduled model.
        # a scheduled model has a FK to the visit instance (source_fk).
        # the rules in this rule group will be evaluated when the source instance
        # is created or saved.
        class TestRuleGroupSched(RuleGroup):
            test_rule = ScheduledDataRule(
                logic=Logic(
                    predicate=(('f1', 'equals', 'No')),
                    consequence='not_required',
                    alternative='new'),
                target_model=['testscheduledmodel2'])

            class Meta:
                app_label = 'testing'
                source_fk = (TestVisit, 'test_visit')
                source_model = TestScheduledModel1
        site_rule_groups.register(TestRuleGroupSched)

        # a test rule group where the source model is a consent or membership model.
        # these models have a FK to registered subject (source_fk).
        # the rules in this rule group will only evaluated when the visit instance
        # is created or saved.
        class TestRuleGroupConsent(RuleGroup):
            test_rule = ScheduledDataRule(
                logic=Logic(
                    predicate=(('may_store_samples', 'equals', 'No')),
                    consequence='not_required',
                    alternative='new'),
                target_model=['testscheduledmodel3'])

            class Meta:
                app_label = 'testing'
                source_fk = (RegisteredSubject, 'registered_subject')
                source_model = TestConsentWithMixin
        site_rule_groups.register(TestRuleGroupConsent)

        class TestRuleGroupConsentFunc(RuleGroup):
            test_rule = ScheduledDataRule(
                logic=Logic(
                    predicate=func_condition_true,
                    consequence='not_required',
                    alternative='new'),
                target_model=['testscheduledmodel3'])

            class Meta:
                app_label = 'testing'
                source_fk = (RegisteredSubject, 'registered_subject')
                source_model = TestConsentWithMixin
#         site_rule_groups.register(TestRuleGroupConsentFunc)

#         class TestRuleGroupConsentFunc2(RuleGroup):
#             test_rule = ScheduledDataRule(
#                 logic=Logic(
#                     predicate=func_condition_false,
#                     consequence='not_required',
#                     alternative='new'),
#                 target_model=['testscheduledmodel3'])
#
#             class Meta:
#                 app_label = 'testing'
#                 source_fk = (RegisteredSubject, 'registered_subject')
#                 source_model = TestConsentWithMixin
#         site_rule_groups.register(TestRuleGroupConsentFunc2)

        self.test_rule_group_rs_cls = TestRuleGroupRs
        self.test_rule_group_sched_cls = TestRuleGroupSched
        self.test_rule_group_consent_cls = TestRuleGroupConsent
        self.test_rule_group_consent_func_cls = TestRuleGroupConsentFunc
#         self.test_rule_group_consent_func2_cls = TestRuleGroupConsentFunc2

        self.test_visit_factory = TestVisitFactory

        self.visit_definition = VisitDefinition.objects.get(code='1000')

        self.test_consent = TestConsentWithMixinFactory(gender='M', study_site=StudySite.objects.all()[0], may_store_samples='No')

        self.registered_subject = RegisteredSubject.objects.get(subject_identifier=self.test_consent.subject_identifier)
        self.appointment = Appointment.objects.get(registered_subject=self.registered_subject)

    def test_get_operator_from_word(self):
        base_rule = BaseRule()
        self.assertRaises(TypeError, base_rule.get_operator_from_word, 'nathan', 1, [1, 2])
        self.assertEqual(base_rule.get_operator_from_word('eq', 1, 1), '==')
        self.assertEqual(base_rule.get_operator_from_word('==', 1, 1), '==')
        self.assertEqual(base_rule.get_operator_from_word('lt', 1, 1), '<')
        self.assertEqual(base_rule.get_operator_from_word('lte', 1, 1), '<=')
        self.assertEqual(base_rule.get_operator_from_word('gt', 1, 1), '>')
        self.assertEqual(base_rule.get_operator_from_word('gte', 1, 1), '>=')
        self.assertEqual(base_rule.get_operator_from_word('lt', 1, 1), '<')
        self.assertEqual(base_rule.get_operator_from_word('lte', 1, 1), '<=')
        self.assertEqual(base_rule.get_operator_from_word('ne', 1, 1), '!=')
        self.assertEqual(base_rule.get_operator_from_word('!=', 1, 1), '!=')
        self.assertEqual(base_rule.get_operator_from_word('in', 1, [1, 2]), 'in')
        self.assertEqual(base_rule.get_operator_from_word('not in', 1, [1, 2]), 'not in')

    def test_meta_attr_with_rs(self):
        """Assert meta attributes of the rule group are set correctly on the rule group."""
        rg = self.test_rule_group_rs_cls()
        self.assertEquals(rg.app_label, 'testing')
        self.assertEquals(rg.source_model, RegisteredSubject)
        self.assertEquals(rg.source_fk_model, None)
        self.assertEquals(rg.source_fk_attr, None)

    def test_meta_attr_with_consent(self):
        """Assert meta attributes of the rule group are set correctly on the rule group."""
        rg = self.test_rule_group_consent_cls()
        self.assertEquals(rg.app_label, 'testing')
        self.assertEquals(rg.source_model, TestConsentWithMixin)
        self.assertEquals(rg.source_fk_model, RegisteredSubject)
        self.assertEquals(rg.source_fk_attr, 'registered_subject')

    def test_meta_attr_with_consent_func(self):
        """Assert meta attributes of the rule group are set correctly on the rule group."""
        rg = self.test_rule_group_consent_func_cls()
        self.assertEquals(rg.app_label, 'testing')
        self.assertEquals(rg.source_model, TestConsentWithMixin)
        self.assertEquals(rg.source_fk_model, RegisteredSubject)
        self.assertEquals(rg.source_fk_attr, 'registered_subject')

    def test_meta_attr(self):
        """Assert meta attributes of the rule group are set correctly on the rule group."""
        rg = self.test_rule_group_sched_cls()
        self.assertEquals(rg.app_label, 'testing')
        self.assertEquals(rg.source_model, TestScheduledModel1)
        self.assertEquals(rg.source_fk_model, TestVisit)
        self.assertEquals(rg.source_fk_attr, 'test_visit')

    def test_rule_attr_with_rs(self):
        """Assert attributes of the rule."""
        rg = self.test_rule_group_rs_cls()
        self.assertEquals(rg.test_rule.source_model, RegisteredSubject)
        self.assertEquals(rg.test_rule.target_model_list, [TestScheduledModel1])
        self.assertEquals(rg.test_rule.source_fk_model, None)
        self.assertEquals(rg.test_rule.source_fk_attr, None)

    def test_rule_attr(self):
        """Assert attributes of the rule."""
        rg = self.test_rule_group_sched_cls()
        self.assertEquals(rg.test_rule.source_model, TestScheduledModel1)
        self.assertEquals(rg.test_rule.target_model_list, [TestScheduledModel2])
        self.assertEquals(rg.test_rule.source_fk_model, TestVisit)
        self.assertEquals(rg.test_rule.source_fk_attr, 'test_visit')

    def test_rule_updates_meta_data_with_rs(self):
        """Assert updates meta data if source is RegisteredSubject."""
        rg = self.test_rule_group_rs_cls()
        self.assertEquals(self.registered_subject.gender, 'M')
        self.assertEqual(ScheduledEntryMetaData.objects.filter(registered_subject=self.registered_subject).count(), 0)
        self.test_visit_factory(appointment=self.appointment)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NOT_REQUIRED, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)

    def test_rule_updates_meta_data_on_update_with_rs(self):
        """Assert updates meta data when the source model is updated."""
        rg = self.test_rule_group_rs_cls()
        self.assertEquals(self.registered_subject.gender, 'M')
        self.assertEqual(ScheduledEntryMetaData.objects.filter(registered_subject=self.registered_subject).count(), 0)
        test_visit = self.test_visit_factory(appointment=self.appointment)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NOT_REQUIRED, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        pk = self.registered_subject.pk
        self.registered_subject.gender = 'F'
        self.registered_subject.save()
        self.registered_subject = RegisteredSubject.objects.get(pk=pk)
        self.assertEquals(self.registered_subject.gender, 'F')
        pk = test_visit.pk
        test_visit = TestVisit.objects.get(pk=pk)
        test_visit.save()  # registered subject does not use a meta data entry manager so you need to re-save the visit
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)

    def test_rule_updates_meta_data_with_consent(self):
        """Assert updates meta data if source is RegisteredSubject and override fields knocked out."""
        rg = self.test_rule_group_consent_cls()
        self.assertEqual(ScheduledEntryMetaData.objects.filter(registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 0)
        self.test_visit_factory(appointment=self.appointment)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NOT_REQUIRED, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)

    def test_rule_updates_meta_data_with_consent_func(self):
        """Assert updates meta data if source is RegisteredSubject and override fields knocked out."""
        site_rule_groups.register(self.test_rule_group_consent_func_cls)
        rg = self.test_rule_group_consent_func_cls()
        self.assertEqual(ScheduledEntryMetaData.objects.filter(registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 0)
        self.test_visit_factory(appointment=self.appointment)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NOT_REQUIRED, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        site_rule_groups.unregister(self.test_rule_group_consent_func_cls)
#     def test_rule_updates_meta_data_with_consent_func2(self):
#         """Assert updates meta data if source is RegisteredSubject and override fields knocked out."""
#         rg = self.test_rule_group_consent_func2_cls()
#         self.assertEqual(ScheduledEntryMetaData.objects.filter(registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 0)
#         self.test_visit_factory(appointment=self.appointment)
#         self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)

    def test_rule_updates_meta_data_on_update_with_consent(self):
        """Assert updates meta data when the source model is updated."""
        rg = self.test_rule_group_consent_cls()
        self.assertEquals(self.test_consent.may_store_samples, 'No')
        self.assertEqual(ScheduledEntryMetaData.objects.filter(registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 0)
        test_visit = self.test_visit_factory(appointment=self.appointment)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NOT_REQUIRED, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        self.test_consent.may_store_samples = 'Yes'
        self.test_consent.save()
        pk = test_visit.pk
        test_visit = TestVisit.objects.get(pk=pk)
        test_visit.save()  # consent does not use a meta data entry manager so you need to re-save the visit
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)

    def test_rule_updates_meta_data(self):
        """Assert updates meta data when source model is created, if criteria met."""
        rg = self.test_rule_group_sched_cls()
        self.assertEqual(ScheduledEntryMetaData.objects.filter(registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 0)
        self.test_visit_factory(appointment=self.appointment)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)

    def test_rule_updates_meta_data2(self):
        """Assert does not update meta data when source model is created, if criteria is not met."""
        rg = self.test_rule_group_sched_cls()
        test_visit = self.test_visit_factory(appointment=self.appointment)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        # set f1=No which is the rule for not required.
        test_scheduled_model1 = TestScheduledModel1Factory(test_visit=test_visit, f1='No')
        # meta data for target, testscheduledmodel2, should be updated as not required
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NOT_REQUIRED, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        test_scheduled_model1.f1 = 'Yes'
        test_scheduled_model1.save()
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)

    def test_rule_updates_meta_data_on_update(self):
        """Assert updates meta data when the source model is updated."""
        rg = self.test_rule_group_sched_cls()
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 0)
        test_visit = self.test_visit_factory(appointment=self.appointment)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        test_scheduled_model1 = TestScheduledModel1Factory(test_visit=test_visit, f1='No')
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NOT_REQUIRED, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)
        test_scheduled_model1.f1 = 'Yes'
        test_scheduled_model1.save()
        self.assertEqual(ScheduledEntryMetaData.objects.filter(entry_status=NEW, registered_subject=self.registered_subject, entry__model_name__in=rg.test_rule.target_model_names).count(), 1)

    def test_rule_updates_meta_data3(self):
        """Asserts repeatedly save visit is harmless."""
        self.test_visit_factory(appointment=self.appointment)
        self.appointment = Appointment.objects.get(registered_subject=self.registered_subject)
        test_visit = TestVisit.objects.get(appointment=self.appointment)
        self.assertIsNone(test_visit.save())
        self.appointment = Appointment.objects.get(registered_subject=self.registered_subject)
        test_visit = TestVisit.objects.get(appointment=self.appointment)
        self.assertIsNone(test_visit.save())
