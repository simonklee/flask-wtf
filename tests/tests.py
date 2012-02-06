from __future__ import with_statement

import unittest

from flask import Flask, render_template, jsonify, Request, request
from flaskext.uploads import UploadSet, IMAGES, TEXT, configure_uploads
from werkzeug.test import EnvironBuilder
from wtforms import StringField, HiddenField, SubmitField, FieldList
from wtforms.validators import Required

from flask.ext.wtf import Form, html5, files

class DummyField(object):
    def __init__(self, data, name='f', label='', id='', type='StringField'):
        self.data = data
        self.name = name
        self.label = label
        self.id = id
        self.type = type

    _value       = lambda x: x.data
    __unicode__  = lambda x: x.data
    __call__     = lambda x, **k: x.data
    __iter__     = lambda x: iter(x.data)
    iter_choices = lambda x: iter(x.data)

class FooForm(Form):
    name = StringField("Name", validators=[Required()])
    submit = SubmitField("Submit")

class HiddenFieldsForm(Form):
    name = HiddenField()
    url = HiddenField()
    method = HiddenField()
    secret = HiddenField()
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(HiddenFieldsForm, self).__init__(*args, **kwargs)
        self.method.name = '_method'

class SimpleForm(Form):
    pass

class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def create_app(self):
        app = Flask(__name__)
        app.secret_key = "secret"

        @app.route("/ajax/", methods=("POST",))
        def ajax_submit():
            form = FooForm(csrf_enabled=False)

            if form.validate_on_submit():
                return jsonify(name=form.name.data, success=True, errors=None)

            return jsonify(name=None, errors=form.errors, success=False)

        return app

    def request(self,*args, **kwargs):
        return self.app.test_request_context(*args, **kwargs)

class HTML5Tests(TestCase):
    field = DummyField("name", id="name", name="name")
    def test_valid(self):
        tests = [
            (html5.URLInput()(self.field), '<input id="name" name="name" type="url" value="name">'),
            (html5.SearchInput()(self.field), '<input id="name" name="name" type="search" value="name">'),
            (html5.DateInput()(self.field), '<input id="name" name="name" type="date" value="name">'),
            (html5.EmailInput()(self.field), '<input id="name" name="name" type="email" value="name">'),
            (html5.NumberInput()(self.field, min=0, max=10), '<input id="name" max="10" min="0" name="name" type="number" value="name">'),
            (html5.NumberInput()(self.field, min=0, max=10), '<input id="name" max="10" min="0" name="name" type="number" value="name">'),
            (html5.RangeInput()(self.field, min=0, max=10), '<input id="name" max="10" min="0" name="name" type="range" value="name">'),
        ]

        for got, expected in tests:
            self.assertEqual(got, expected)

# FILE UPLOAD TESTS #

images = UploadSet("images", IMAGES)
text = UploadSet("text", TEXT)

class FileUploadForm(Form):
    upload = files.FileField("Upload file")

class MultipleFileUploadForm(Form):
    uploads = FieldList(files.FileField("upload"), min_entries=3)

class ImageUploadForm(Form):
    upload = files.FileField("Upload file",
                       validators=[files.file_required(),
                                   files.file_allowed(images)])

class TextUploadForm(Form):
    upload = files.FileField("Upload file",
                       validators=[files.file_required(),
                                   files.file_allowed(text)])

class TestFileUpload(TestCase):
    def create_app(self):
        app = super(TestFileUpload, self).create_app()
        app.config['CSRF_ENABLED'] = False
        app.config['UPLOADED_FILES_DEST'] = 'uploads'
        app.config['UPLOADS_DEFAULT_DEST'] = 'uploads'
        configure_uploads(app, [images, text])

        @app.route("/upload-image/", methods=("POST",))
        def upload_image():
            form = ImageUploadForm()
            if form.validate_on_submit():
                return "OK"
            return "invalid"

        @app.route("/upload-text/", methods=("POST",))
        def upload_text():
            form = TextUploadForm()
            if form.validate_on_submit():
                return "OK"
            return "invalid"

        @app.route("/upload-multiple/", methods=("POST",))
        def upload_multiple():
            form = MultipleFileUploadForm()

            if form.validate_on_submit():
                assert len(form.uploads.entries) == 3

                for upload in form.uploads.entries:
                    assert upload.file is not None

            return "OK"

        @app.route("/upload/", methods=("POST",))
        def upload():
            form = FileUploadForm()

            if form.validate_on_submit():

                filedata = form.upload.file
            else:
                filedata = None

            return render_template("upload.html",
                                   filedata=filedata,
                                   form=form)
        return app

    def test_multiple_files(self):
        fps = [self.app.open_resource("flask.png") for i in xrange(3)]
        data = [("uploads-%d" % i, fp) for i, fp in enumerate(fps)]
        response = self.client.post("/upload-multiple/", data=dict(data))
        assert response.status_code == 200

    def test_valid_file(self):
        with self.app.open_resource("flask.png") as fp:
            response = self.client.post("/upload-image/",
                data={'upload' : fp})

        assert "OK" in response.data

    def test_missing_file(self):
        response = self.client.post("/upload-image/",
                data={'upload' : "test"})

        assert "invalid" in response.data

    def test_invalid_file(self):
        with self.app.open_resource("flask.png") as fp:
            response = self.client.post("/upload-text/",
                data={'upload' : fp})

        assert "invalid" in response.data


    def test_invalid_file_upload(self):
        response = self.client.post("/upload/",
                data={'upload' : 'flask.png'})

        assert "flask.png</h3>" not in response.data

class TestValidateOnSubmit(TestCase):
    def test_not_submitted(self):
        with self.request(method='GET', data={}):
            f = FooForm(request.form, csrf_enabled=False)
            self.assertEqual(f.is_submitted(), False)
            self.assertEqual(f.validate_on_submit(), False)

    def test_submitted_not_valid(self):
        with self.request(method='POST', data={}):
            f = FooForm(request.form, csrf_enabled=False)
            self.assertEqual(f.is_submitted(), True)
            self.assertEqual(f.validate(), False)

    def test_submitted_and_valid(self):
        with self.request(method='POST', data={'name':'foo'}):
            f = FooForm(request.form, csrf_enabled=False)
            self.assertEqual(f.validate_on_submit(), True)

class TestHiddenTag(TestCase):
    def test_hidden_tag(self):
        with self.request(method='POST'):
            f = HiddenFieldsForm(request.form)
            self.assertEqual(f.hidden_fields().count('type="hidden'), 5)

class TestCSRF(TestCase):
    def test_csrf_token(self):
        with self.request(method='GET'):
            f = FooForm(request.form)
            self.assertEqual(hasattr(f, 'csrf_token'), True)
            self.assertEqual(f.validate(), False)

    def test_invalid_csrf(self):
        with self.request(method='POST', data={'name':'foo'}):
            f = FooForm()
            self.assertEqual(f.validate_on_submit(), False)
            self.assertEqual(f.errors['csrf_token'], [u'CSRF token missing'])

    def test_csrf_disabled(self):
        self.app.config['CSRF_ENABLED'] = False

        with self.request(method='POST', data={'name':'foo'}):
            f = FooForm(request.form)
            f.validate()
            self.assertEqual(f.validate_on_submit(), True)

    def test_valid(self):
        csrf_token = FooForm().csrf_token.current_token
        builder = EnvironBuilder(method='POST', data={'name':'foo', 'csrf_token': csrf_token })
        env = builder.get_environ()
        req = Request(env)
        f = FooForm(req.form)
        self.assertTrue(f.validate())

    def test_ajax(self):
        # TODO: actually test this, only checks return value,
        # form does not validate with CSRF
        response = self.client.post("/ajax/",
                                    data={"name" : "danny"},
                                    headers={'X-Requested-With' : 'XMLHttpRequest'})
        assert response.status_code == 200
