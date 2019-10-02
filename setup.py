# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
import watson.framework

name = 'watson-framework'
description = 'A Python 3 web app framework.'
version = watson.framework.__version__


def read(filename, as_list=False):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        contents = f.read()
        if as_list:
            return contents.splitlines()
        return contents


setup(
    name=name,
    version=version,
    url='http://github.com/watsonpy/' + name,
    description=description,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',

    author='Simon Coulton',
    author_email='simon@bespohk.com',

    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'watson-console = watson.framework.bin:main'
        ]
    },
    install_requires=read('requirements.txt', as_list=True),
    extras_require={
        'test': read('requirements-test.txt', as_list=True)
    },
)
