from .rule import Rule


class CrfRule(Rule):

    def __init__(self, target_models, **kwargs):
        self.rule_type = 'crf'
        self.target_models = target_models
        super(CrfRule, self).__init__(**kwargs)
