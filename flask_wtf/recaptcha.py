from __future__ import absolute_import

import urllib2
import wtforms

from flask import request, current_app
from wtforms import Field
from werkzeug import url_encode

try:
    import json
except ImportError:
    import simplejson as json

try:
    from flaskext.babel import gettext as _
except ImportError:
    _ = lambda(s) : s

RECAPTCHA_VERIFY_SERVER = 'http://api-verify.recaptcha.net/verify'
RECAPTCHA_API_SERVER = 'http://api.recaptcha.net/'
RECAPTCHA_SSL_API_SERVER = 'https://api-secure.recaptcha.net/'
RECAPTCHA_HTML = u'''
<script type="text/javascript">var RecaptchaOptions = %(options)s;</script>
<script type="text/javascript" src="%(script_url)s"></script>
<noscript>
  <div><iframe src="%(frame_url)s" height="300" width="500"></iframe></div>
  <div><textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
  <input type="hidden" name="recaptcha_response_field" value="manual_challenge"></div>
</noscript>
'''

class Recaptcha(object):
    """Validates a ReCaptcha."""
    _error_codes = {
        'invalid-site-public-key': 'The public key for reCAPTCHA is invalid',
        'invalid-site-private-key': 'The private key for reCAPTCHA is invalid',
        'invalid-referrer': 'The public key for reCAPTCHA is not valid for '
            'this domainin',
        'verify-params-incorrect': 'The parameters passed to reCAPTCHA '
            'verification are incorrect',
    }

    def __init__(self, message=u'Invalid word. Please try again.'):
        self.message = message

    def __call__(self, form, field):
        challenge = request.form.get('recaptcha_challenge_field', '')
        response = request.form.get('recaptcha_response_field', '')
        remote_ip = request.remote_addr

        if not challenge or not response:
            raise wtforms.ValidationError('This field is required.')

        if not self._validate_recaptcha(challenge, response, remote_ip):
            field.recaptcha_error = 'incorrect-captcha-sol'
            raise wtforms.ValidationError(self.message)

    def _validate_recaptcha(self, challenge, response, remote_addr):
        """Performs the actual validation."""

        if current_app.testing:
            return True

        try:
            private_key = current_app.config['RECAPTCHA_PRIVATE_KEY']
        except KeyError:
            raise RuntimeError, "No RECAPTCHA_PRIVATE_KEY config set"

        data = url_encode({
            'privatekey': private_key,
            'remoteip':   remote_addr,
            'challenge':  challenge,
            'response':   response
        })

        response = urllib2.urlopen(RECAPTCHA_VERIFY_SERVER, data)

        if response.code != 200:
            return False

        rv = [l.strip() for l in response.readlines()]

        if rv and rv[0] == 'true':
            return True

        if len(rv) > 1:
            error = rv[1]
            if error in self._error_codes:
                raise RuntimeError(self._error_codes[error])

        return False

recaptcha = Recaptcha

class RecaptchaWidget(object):
    def recaptcha_html(self, server, query, options):
        return RECAPTCHA_HTML % dict(
            script_url='%schallenge?%s' % (server, query),
            frame_url='%snoscript?%s' % (server, query),
            options=json.dumps(options)
        )

    def __call__(self, field, error=None, **kwargs):
        """Returns the recaptcha input HTML."""

        if current_app.config.get('RECAPTCHA_USE_SSL', False):

            server = RECAPTCHA_SSL_API_SERVER

        else:

            server = RECAPTCHA_API_SERVER

        try:
            public_key = current_app.config['RECAPTCHA_PUBLIC_KEY']
        except KeyError:
            raise RuntimeError, "RECAPTCHA_PUBLIC_KEY config not set"
        query_options = dict(k=public_key)

        if field.recaptcha_error is not None:
            query_options['error'] = unicode(field.recaptcha_error)

        query = url_encode(query_options)

        options = {
           'theme': 'clean',
            'custom_translations': {
                'visual_challenge':    _('Get a visual challenge'),
                'audio_challenge':     _('Get an audio challenge'),
                'refresh_btn':         _('Get a new challenge'),
                'instructions_visual': _('Type the two words:'),
                'instructions_audio':  _('Type what you hear:'),
                'help_btn':            _('Help'),
                'play_again':          _('Play sound again'),
                'cant_hear_this':      _('Download sound as MP3'),
                'incorrect_try_again': _('Incorrect. Try again.'),
            }
        }

        options.update(current_app.config.get('RECAPTCHA_OPTIONS', {}))
        return self.recaptcha_html(server, query, options)

class RecaptchaField(Field):
    widget = RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(self, label='', validators=None, **kwargs):
        validators = validators or [Recaptcha()]
        super(RecaptchaField, self).__init__(label, validators, **kwargs)
