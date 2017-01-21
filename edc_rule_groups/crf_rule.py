from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .rule import Rule


class VisitScheduleRule(Rule):

    visit_schedule_name = None
    schedule_name = None
    visit_codes = None

    def __init__(self, visit_schedule_name=None, schedule_name=None,
                 visit_codes=None, **kwargs):
        super().__init__(**kwargs)
        self.visit_codes = visit_codes

    @property
    def visits(self):
        visits = []
        self.visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
        if self.visit_schedule:
            self.schedule = self.visit_schedule.schedules.get(self.schedule_name)
            if self.schedule:
                visits = (
                    v for v in self.schedule.visits
                    if v.code in self.visit_codes or [])
        return visits

    def runif(self, visit, **kwargs):
        return True if visit.visit_code in [visit.code for visit in self.visits] else False


class CrfRule(VisitScheduleRule):

    def __init__(self, target_models, visit_codes=None, **kwargs):
        super().__init__(target_models, visit_codes, **kwargs)
        self.rule_type = 'crf'
        self.target_models = target_models
