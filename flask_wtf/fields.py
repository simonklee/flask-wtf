from __future__ import with_statement, absolute_import

from flask import request
from wtforms import FileField as _FileField
from wtforms.fields import Field

from .widgets import RecaptchaWidget
from .validators import Recaptcha

__all__ = ['FileField', 'RecaptchaField']

class RecaptchaField(Field):
    widget = RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(self, label='', validators=None, **kwargs):
        validators = validators or [Recaptcha()]
        super(RecaptchaField, self).__init__(label, validators, **kwargs)

class FileField(_FileField):
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
