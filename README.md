# edc-rule-groups

This app is now part of `edc_metadata`.

To update your project:

* `pip uninstall edc-rule-groups`
* remove `edc_rule_groups.apps.AppConfig` from `INSTALLED_APPS`
* Rename `rule_groups.py` to `metadata_rules.py`
* update imports in  `metadata_rules.py` by replacing `from edc_rule_groups. ...` 
  with `from edc_metadata.rules. ...`
* you may also need to update imports for `models`, specifically your visit model,
  crf model mixin and requisition model mixin.

`edc_metadata` now imports rules from it's `AppConfig.ready`. 