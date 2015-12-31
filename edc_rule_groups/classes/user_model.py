from django.db.models import get_model, Model


class UserModel(object):

    def __init__(self, *args, **kwargs):
        if 'app_label' in kwargs and 'model_name' in kwargs:
            self.model_cls = get_model(kwargs.get('app_label'), kwargs.get('model_name'))
        if 'model' in kwargs:
            model = kwargs.get('model')
            if isinstance(model, tuple):
                self.model_cls = get_model(model[0], model[1])
            elif isinstance(model, Model):
                self.model_cls = model
            else:
                AttributeError('Attribute \'model\' must be a tuple of (app_label, model_name)')
        elif args:
            self.model_cls = args[0]
        else:
            pass
        if not self.model_cls:
            raise AttributeError(
                'Unable to set user model_cls. Need either kwargs \'app_label\' and '
                '\'model_name\' or the user model class as an arg or tuple.')
        if 'field_name' in kwargs:
            self.field_name = kwargs.get('field_name')
        else:
            raise AttributeError('Unable to set user model field name. Need kwarg field_name.')
