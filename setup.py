from setuptools import setup
from djparsing import __author__, __version__

setup(
    name='djparsing',
    description='Convenient parser with saving data to the database',
    version=__version__,
    packages=['djparsing'],
    author=__author__,
    author_email='vlinchevskyi@gmail.com',
    license='BSD License',
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
