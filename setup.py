from setuptools import setup
from setuptools import find_packages


def requirements(path):
    with open(path) as req:
        return [x.strip() for x in req.readlines() if not x.startswith('-')]


setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    description='Pandas-ORM Integration.',
    install_requires=requirements('requirements.txt'),
    name='redpanda',
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/redpanda',
    use_scm_version=True,
)
