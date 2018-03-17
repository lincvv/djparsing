import os
from setuptools import setup
from djparsing import __author__, __version__


def __read_requires(file):
    try:
        return open(os.path.join(os.path.dirname(__file__), file)).read()
    except IOError:
        return ''


install_requires = __read_requires("requirements.txt").split()

setup(
    name='djparsing',
    description='microframework for parsing sites, '
                'a simple interface and flexibility will help you quickly start parsing sites.',
    version=__version__,
    packages=['djparsing'],
    author=__author__,
    author_email='vlinchevskyi@gmail.com',
    license='BSD License',
    install_requires=install_requires,
    url='https://github.com/lincvv/djparsing',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
)
