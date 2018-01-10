# coding: utf-8
import sys

from setuptools import find_packages, setup

test_requirements = ['responses',
                     'pytest-cov',
                     'pytest-mock',
                     'pytest>=2.8.0', ]

install_requires = ['six',
                    'requests<3.0.0',
                    'future']

if sys.version_info == (2, 7):
    install_requires.append('functools32')

setup(
    name='thrall',
    version='0.0.23',
    description='Maps web-service HTTP Api',
    author='Zoltan Qin',
    author_email='qinzezzhen@outlook.com',
    packages=find_packages(exclude=('benchmarks',)),
    tests_require=test_requirements,
    install_requires=install_requires,
)
