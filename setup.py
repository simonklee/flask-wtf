"""
Flask-WTF
---------

Simple integration of Flask and WTForms, including CSRF, file upload
and Recaptcha integration.
"""
from setuptools import setup

setup(
    name='Flask-WTF',
    version='0.6.4',
    url='http://github.org/simonz05/flask-wtf',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    description='Simple integration of Flask and WTForms',
    long_description=__doc__,
    packages=['flask_wtf'],
    test_suite='nose.collector',
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    dependency_links=['https://bitbucket.org/simplecodes/wtforms/get/tip.tar.gz#egg=wtforms-0.6.4dev'],
    install_requires=[
        'Flask',
        'wtforms>=0.6.4dev'
    ],
    tests_require=[
        'nose',
        'Flask-Uploads',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
