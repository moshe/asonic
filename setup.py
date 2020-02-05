import sys

from setuptools import setup

if sys.version_info.major == 2:
    raise RuntimeError('python2 is not supported')

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except Exception:
    long_description = ''

setup(
    name='asonic',
    author='Moshe Zada',
    version='2.0.0',
    packages=['asonic'],
    keywords=['asonic', 'sonic', 'search', 'asyncio', 'async', 'text'],
    url='https://github.com/moshe/asonic',
    license='MPL-2.0',
    long_description=long_description,
    description='Async python client for Sonic database',
    install_requires=[],
    extras_require={
        'tests': ['pytest', 'pytest-asyncio', 'flake8'],
    },
)
