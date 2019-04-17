from setuptools import setup
from setuptools import find_packages


def requirements(path):
    with open(path) as req:
        return [x.strip() for x in req.readlines() if not x.startswith('-')]


setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Pandas-ORM Integration.',
    install_requires=requirements('requirements.txt'),
    name='redpanda',
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/redpanda',
    use_scm_version=True,
)
