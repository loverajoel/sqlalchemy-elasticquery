"""
    SQLAlchemy-ElasticQuery
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Permite usar la sintaxis de busqueda de ES en SQLAlchemy.
    Crea un objeto SQLAlchemy query y devuelve la query lista

    :copyright: 2015 Joel Lovera <joelalovera@gmail.com>
    :license: GNU AGPLv3+ or BSD
"""

from sqlalchemy import and_
from sqlalchemy import or_

__version__ = '0.0.1'

def elastic_query():
    return True