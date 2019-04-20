from setuptools import setup
from setuptools import find_packages

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Pandas-ORM Integration.',
    install_requires=[
        'pandas >= 0.16',
        'sqlalchemy >= 1.3',
    ],
    name='redpanda',
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/redpanda',
    use_scm_version=True,
)
