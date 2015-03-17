# sqlalchemy-elasticquery

Use [ElasticSearch](http://www.elasticsearch.org/) syntax for search in [SQLAlchemy](http://www.sqlalchemy.org/).

WARNING: ElasticQuery is currently under active development.  Thus the format of the API and this module may change drastically.

# Install
```
pip install sqlalchemy-elasticquery
```
# Quick start example
Import module
```python
from sqlalchemy_elasticquery import elastic_query
```

SQLAlchemy imports
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_elasticquery import elastic_query
```

Setup SQLAlchemy
```python
engine = create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
```

Model example
```python
class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	lastname = Column(String)
	uid = Column(Integer)
```

Create DB and add mock data
```python
Base.metadata.create_all(bind=engine)
session.add_all([
	User(name='Jhon', lastname='Galt', uid='19571957'),
	User(name='Steve', lastname='Jobs', uid='20092009'),
	User(name='Iron', lastname='Man', uid='19571957')
])
session.commit()
```

ElasticQuery example
```python
query_string = '{"filter":{"or":{"name":"Jhon","lastname":"Galt"},"and":{"uid":"19571957"}}}'
print elastic_query(User, query_string, session)
SELECT users.id AS users_id, users.name AS users_name, users.lastname AS users_lastname, users.uid AS users_uid FROM users WHERE users.uid = :uid_1 AND (users.lastname = :lastname_1 OR users.name = :name_1)
```
# Querying
* ***Nested search***: You can search for nested properties(Two levels, now). Ex: 

# Options

* **enabled_fields**: It's a list of fields allowed for work, for default all fields are allowed.

# Using with Flask

ElasticQuery example
```python
from sqlalchemy_elasticquery import elastic_query

query_string = '{"filter":{"or":{"name":"Jhon","lastname":"Galt"},"and":{"uid":"19571957"}}}'
print elastic_query(User, query_string)
SELECT users.id AS users_id, users.name AS users_name, users.lastname AS users_lastname, users.uid AS users_uid FROM users WHERE users.uid = :uid_1 AND (users.lastname = :lastname_1 OR users.name = :name_1)
```

# TODO:
 - Improve documentation
 - Improve tests
 - Errors emit