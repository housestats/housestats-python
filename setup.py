from setuptools import setup, find_packages

setup(
    name='housestats',
    version='0.1',
    author='Lars Kellogg-Stedman',
    author_email='lars@oddbit.com',
    description='wrapper for fetching metrics from remote apis',
    license='GPLv3',
    url='https://github.com/larsks/housestats',
    packages=find_packages(),
    entry_points={
        'housestats.sensor': [
            'example=housestats.sensor.example:ExampleSensor',
        ],
        'console_scripts': [
            'housestats=housestats.main:cli',
        ]
    }
)
