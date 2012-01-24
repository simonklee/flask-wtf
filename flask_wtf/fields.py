from __future__ import with_statement, absolute_import

import wtforms
from flask import request
from wtforms.fields import *

from .widgets import RecaptchaWidget
from .validators import Recaptcha

__all__ = ['FileField', 'RecaptchaField']
__all__ += wtforms.fields.core.__all__
__all__ += wtforms.fields.simple.__all__

try:
    import sqlalchemy
    from wtforms.ext.sqlalchemy.fields import QuerySelectField, \
        QuerySelectMultipleField

    __all__ += ['QuerySelectField',
                'QuerySelectMultipleField']
except ImportError:
    pass

class RecaptchaField(wtforms.Field):
    widget = RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(self, label='', validators=None, **kwargs):
        validators = validators or [Recaptcha()]
        super(RecaptchaField, self).__init__(label, validators, **kwargs)

class FileField(wtforms.FileField):
    """
    Subclass of **wtforms.FileField** providing a `file` property
    returning the relevant **FileStorage** instance in **request.files**.
    """
    @property
    def file(self):
        """
        Returns FileStorage class if available from request.files
        or None
        """
        return request.files.get(self.name, None)
