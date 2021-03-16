from setuptools import find_packages
from setuptools import setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Database',
        'Topic :: Utilities',
    ],
    description='Pandas-ORM Integration.',
    install_requires=[
        'pandas >= 0.16',
        'sqlalchemy >= 1.3',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='redpanda',
    packages=find_packages(exclude=['tests']),
    python_requires='>= 3.5',
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
