from setuptools import setup, find_packages
from codecs import open
from os import path

here=path.abspath(path.dirname(__file__))
with open(path.join(here,'README.srt'),encoding='utf-8') as f:
    long_description=f.read()

setup(
    name='combatmanager',
    version=1.0,
    description='Graphical interface for managing combat in a certain role-playing game',
    long_description=long_description,
    author='Mathias',
    license='GPL',
    classifiers=[
        'Development Status :: 4-Beta'
        'Topic :: Games/Entertainment :: Role-Playing'
        'License :: OSI Approved :: GNU General Public License (GPL)'
        'Programming Language :: Python :: 3'
    ],
    keywords='role-playing combat management',
    packages=find_packages(exclude=['Backup','Fights','Monsters']),
    entry_points={
        'gui_scripts' : [
            'combatmanager=combatmanager:start'
        ]
    }

)