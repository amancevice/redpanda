import textwrap
from setuptools import setup

setup(name='redpanda',
      version='0.4.0',
      author='amancevice',
      author_email='smallweirdnum@gmail.com',
      packages=['redpanda'],
      url='http://www.smallweirdnumber.com',
      description='Pandas-ORM Integration.',
      long_description=textwrap.dedent(
          '''See GitHub_ for documentation.
          .. _GitHub: https://github.com/amancevice/redpanda'''),
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Topic :: Utilities',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python'],
      install_requires=['pandas>=0.16.0', 'sqlalchemy>=1.1.10'])
