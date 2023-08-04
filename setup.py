from setuptools import setup

setup(
    name='postget',
    version='1.1.2',
    description='Posts getter',
    author='',
    author_email='',
    packages=['postget', 'postget.exceptions'],
    entry_points={
        'console_scripts': [
            'postget=postget.main:main'
        ]
    }
)