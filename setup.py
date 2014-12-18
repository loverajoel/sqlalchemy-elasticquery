import os

from setuptools import setup

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='sqlalchemy_elasticquery',
    version='0.0.1',
    description='Use ElasticSearch query search in SQLAlchemy.',
    url='https://github.com/loverajoel/sqlalchemy-elasticquery',
    license='MIT',
    author='Lovera Joel',
    author_email='joelalover@gmail.com',
    packages=['sqlalchemy_elasticquery'],
    include_package_data=True,
    install_requires=[
        'SQLAlchemy>=0.7.8',
    ]
)
