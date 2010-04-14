import os
from setuptools import setup, find_packages

def read(fname):
    '''Return the contents of the named file.'''

    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def read_version():
    '''Read version information from the spec file.'''

    for line in open('ganglia-plugin-iptables.spec'):
        if line.startswith('Version:'):
            return line.split()[-1]

setup(name='ganglia-plugin-iptables',
        version=read_version(),
        description='iptables plugin for ganglia',
        long_description=read('README.rst'),
        author='Lars Kellogg-Stedman',
        author_email='lars@seas.harvard.edu',
        packages=['ganglia_iptables'],
        scripts=['iptables.py'],
        )

