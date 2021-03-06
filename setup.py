import sys
from distutils.core import setup

required = []

if sys.version_info[:3] < (2, 6, 0):
    required.append('simplejson')

setup(
    name='dropio',
    version='0.1.1',
    description='A Python client library for the Drop.io API',
    author='Jimmy Orr',
    license='GPLv3',
    url='https://github.com/jimmyorr/dropio-api-python',
    packages=['dropio'],
    package_dir={'dropio':'src/dropio'},
    requires=required,
    scripts=['scripts/dropio']
)
