# -*- coding: utf-8 -*-
from __future__ import absolute_import

import wtforms
from wtforms.fields import *
from wtforms.validators import *
from wtforms.widgets import *
from . import html5
from .fields import *
from .form import *
from .validators import *
from .widgets import *

__all__  = ['wtforms.ValidationError', 'html5']
__all__ += wtforms.fields.core.__all__
__all__ += wtforms.widgets.core.__all__
__all__ += wtforms.validators.__all__
__all__ += fields.__all__
__all__ += form.__all__
__all__ += validators.__all__
__all__ += widgets.__all__

try:
    import sqlalchemy
    from wtforms.ext.sqlalchemy.fields import QuerySelectField, \
        QuerySelectMultipleField

    __all__ += ['QuerySelectField',
                'QuerySelectMultipleField']

    for field in (QuerySelectField,
                  QuerySelectMultipleField):

        setattr(fields, field.__name__, field)
except ImportError:
    pass
