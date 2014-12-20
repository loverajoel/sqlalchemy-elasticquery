# sqlalchemy-elasticquery

Use [ElasticSearch](http://www.elasticsearch.org/) query search in [SQLAlchemy](http://www.sqlalchemy.org/).

WARNING: ElasticQuery is currently under active development.  Thus the format of the API and this module may change drastically.

# Install
``` 
sudo pip install git+https://github.com/loverajoel/sqlalchemy-elasticquery 
```
# Quick start example
Import module
``` 
>>> from sqlalchemy_elasticquery import elastic_query
```
SQLAlchemy imports
``` 
>>> from sqlalchemy import create_engine, Column, Integer, String
>>> from sqlalchemy.ext.declarative import declarative_base
>>> from sqlalchemy.orm import sessionmaker
>>> from sqlalchemy_elasticquery import elastic_query
```
Setup SQLAlchemy
```
>>> engine = create_engine('sqlite:///:memory:', echo=False)
>>> Session = sessionmaker(bind=engine)
>>> session = Session()
>>> Base = declarative_base()
```

Model example
```
>>> class User(Base):
... __tablename__ = 'users'
... id = Column(Integer, primary_key=True)
... name = Column(String)
... lastname = Column(String)
... uid = Column(Integer)
```

Create db and add mock data
```
>>> Base.metadata.create_all(bind=engine)
>>> session.add_all([
... User(name='Jhon', lastname='Galt', uid='19571957'),
... User(name='Steve', lastname='Jobs', uid='20092009'),
... User(name='Iron', lastname='Man', uid='19571957')
])
>>> session.commit()
```
ElasticQuery example
```
>>> query_string = '{"filter":{"or":{"name":"Jhon","lastname":"Galt"},"and":{"uid":"19571957"}}}'
>>> print elastic_query(User, query_string, session)
SELECT users.id AS users_id, users.name AS users_name, users.lastname AS users_lastname, users.uid AS users_uid FROM users WHERE users.uid = :uid_1 AND (users.lastname = :lastname_1 OR users.name = :name_1)
```
# Querying

# Using with Flask

# TODO:
 - Sorting support
 - Operator leveles (and : { or : {...}}
 - Improve documentation
 - Improve tests
 - Flask supporr
 - Errors emit