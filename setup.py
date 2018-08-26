from setuptools import setup

setup(name='redpanda',
      use_scm_version=True,
      author='amancevice',
      author_email='smallweirdnum@gmail.com',
      packages=['redpanda'],
      url='http://www.smallweirdnumber.com',
      description='Pandas-ORM Integration.',
      long_description='See GitHub_ for documentation.'
                       '.. _GitHub: https://github.com/amancevice/redpanda',
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      setup_requires=['setuptools_scm'],
      install_requires=['pandas >= 0.16.0', 'sqlalchemy >= 1.1.10'])
