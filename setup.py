from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytimebox',
    version='1.0.0',
    description='Control interface for the divoo timebox',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chance-nelson/pytimebox',
    author='Chance Nelson',
    author_email='github@chancen.xyz',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    keywords='divoo timebox pytimebox',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
