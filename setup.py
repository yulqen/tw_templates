#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'parsedatetime>=2.4', ]

setup_requirements = ['pytest-runner', 'pytest-mypy' ]

test_requirements = ['pytest', ]

setup(
    author="Matthew Lemon",
    author_email='matt@matthewlemon.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Create taskwarrior tasks based on templates.",
    entry_points={
        'console_scripts': [
            'tw_templates=tw_templates.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='tw_templates',
    name='tw_templates',
    packages=find_packages(include=['tw_templates']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/hammerheadlemon/tw_templates',
    version='0.1.0',
    zip_safe=False,
)
