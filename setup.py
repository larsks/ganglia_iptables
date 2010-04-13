import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='ganglia_iptables',
        version='20100413.1',
        description='iptables plugin for ganglia',
        author='Lars Kellogg-Stedman',
        author_email='lars@seas.harvard.edu',
        packages=['ganglia_iptables'],
        )

