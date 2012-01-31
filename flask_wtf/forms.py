from __future__ import absolute_import

import jinja2

from flask import request, session, current_app
from wtforms.ext.csrf.session import SessionSecureForm
from wtforms.fields import HiddenField

class Form(SessionSecureForm):
    "Implements a SessionSecureForm using app.SECRET_KEY and flask.session obj"
    def __init__(self, formdata=None, obj=None, prefix='', csrf_enabled=None, **kwargs):
        self.csrf_enabled = csrf_enabled

        if csrf_enabled is None:
            self.csrf_enabled = current_app.config.get('CSRF_ENABLED', True)

        self.SECRET_KEY = current_app.config.get('CSRF_SESSION_KEY', '_csrf_token')
        super(Form, self).__init__(formdata, obj, prefix, session, **kwargs)

    def is_submitted(self):
        "Check if request method is either PUT or POST"
        return request and request.method in ("PUT", "POST")

    def validate_on_submit(self):
        "Call `form.validate()` if request method was either PUT or POST"
        return self.is_submitted() and self.validate()

    def validate_csrf_token(self, field):
        if not self.csrf_enabled:
            return True

        return super(Form, self).validate_csrf_token(field)

    def hidden_fields(self, *fields):
        "hidden fields in a hidden DIV tag, in order to keep XHTML compliance."
        if not fields:
            fields = [f for f in self if isinstance(f, HiddenField)]

        rv = [u'<div style="display:none;">']

        for field in fields:
            if isinstance(field, basestring):
                field = getattr(self, field)
            rv.append(unicode(field))

        rv.append(u"</div>")

        return jinja2.Markup(u"".join(rv))

    def process(self, formdata=None, obj=None, **kwargs):
        try:
            if formdata is None:
                formdata = request.form
        except AttributeError:
            pass
        super(Form, self).process(formdata, obj, **kwargs)
