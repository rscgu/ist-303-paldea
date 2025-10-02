#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from setuptools import setup

setup(
    name = 'my_paldea',
    version = '1.0',
    license='GNU General Public Licence v3',
    author='Gerves Baniakina',
    author_email='gerves-francois.baniakina@cgu.edu',
    description=' Personal Financial Budget Planning',
    packages=['my_paldea'],
    platforms='any',
    install_requires=['Flask', ],
    classifiers=[
        'Development Status :: 4 -Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'

    ],
)
