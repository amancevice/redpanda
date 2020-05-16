from setuptools import find_packages
from setuptools import setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Pandas-ORM Integration.',
    install_requires=[
        'pandas >= 0.16',
        'sqlalchemy >= 1.3',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='redpanda',
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_scm'],
    tests_require=[
        'flake8',
        'pytest',
        'pytest-cov',
        'randomwords',
    ],
    url='https://github.com/amancevice/redpanda',
    use_scm_version=True,
)
