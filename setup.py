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
    version='0.1.0',
    packages=['asonic'],
    keywords=['asonic', 'sonic', 'search', 'asyncio', 'async', 'text'],
    url='https://github.com/moshe/asonic',
    license='',
    long_description=long_description,
    description='Async python client for Sonic database',
    install_requires=[],
)
