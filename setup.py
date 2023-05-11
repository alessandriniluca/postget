from setuptools import setup

setup(
    name='postget',
    version='0.3.1',
    description='Posts getter',
    author='',
    author_email='',
    packages=['postget'],
    entry_points={
        'console_scripts': [
            'postget=postget.main:main'
        ]
    }
)