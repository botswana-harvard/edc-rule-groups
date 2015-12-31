

class Logic(object):

    def __init__(self, *args, **kwargs):
        if args:
            if ((isinstance(args[0], (tuple, list)) or hasattr(args[0], '__call__')) and len(args[0]) == 3):
                self.predicate, self.consequence, self.alternative = args[0]
            else:
                raise AttributeError(
                    'Attribute \'logic\' must be a tuple of (predicate, consequence, alternative) or callable')
        else:
            self.predicate = kwargs.get('predicate')
            self.consequence = kwargs.get('consequence')
            self.alternative = kwargs.get('alternative')
            self.comment = kwargs.get('comment') or ''

    @property
    def __doc__(self):
        if hasattr(self.predicate, '__call__'):
            predicate_items = [self.predicate.__doc__]
            return ('{0}. If True sets \'{{target_model}}\' to \'{1.consequence}\' otherwise \'{1.alternative}\'. '
                    '{1.comment}').format(
                        (self.predicate.__doc__ or '<font color="red">missing docstring</font>'
                         ).strip('\n\r\t').replace('\n', ''), self)
        else:
            predicate_items = []
            predicate = self.predicate if isinstance(self.predicate[0], tuple) else (self.predicate, )
            for item in predicate:
                try:
                    predicate_items.append(item[3].upper())
                except IndexError:
                    pass
                predicate_items.append(' '.join([str(x) for x in item[0:3]]))
            return ('Returns True if {0}. If True sets \'{{target_model}}\' to \'{1.consequence}\' otherwise '
                    '\'{1.alternative}\'. {1.comment}').format(' '.join(predicate_items), self)
