import unittest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_elasticquery import elastic_query

from sqlalchemy import and_, or_

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    uid = Column(Integer)

    def __repr__(self):
        return str(self.id)

class TestCase(unittest.TestCase):

    def setUp(self):
        """ Initial setup for the test"""
        global engine
        engine = create_engine('sqlite:///:memory:', echo=False)
        global Session
        Session = sessionmaker(bind=engine)
        global session
        session = Session()

        Base.metadata.create_all(bind=engine)

        session.add_all([
        User(name='Jhon', lastname='Galt', uid='19571957'),
        User(name='Steve', lastname='Jobs', uid='20092009'),
        User(name='Iron', lastname='Man', uid='19571957')
        ])
        session.commit()

    def test_setup_is_ok(self):
        """ Demo test """
        assert(session.query(User).count() == 3)
        # print session.query(User).filter(or_(User.name == "Jhone", User.name == "Jhone" ))

    def test_simple_query(self):
        """ test simple query """
        query_string = '{"filter" : {"uid" : {"like" : "%1957%"} } }'
        assert(elastic_query(User, query_string, session).count() == 2)
        query_string = '{"filter" : {"name" : {"like" : "%Jho%"}, "lastname" : "Galt" } }'
        assert(elastic_query(User, query_string, session).count() == 1)

    def test_and_operator(self):
        """ test and operator """
        query_string = '{"filter" : {"and" : {"name" : {"like" : "%Jho%"}, "lastname" : "Galt", "uid" : {"like" : "%1957%"} } } }'
        assert(elastic_query(User, query_string, session).count() == 1)

    def test_or_operator(self):
        """ test or operator """
        query_string = '{"filter" : {"or" : { "name" : "Jobs", "lastname" : "Man", "uid" : "19571957" } } }'
        assert(elastic_query(User, query_string, session).count() == 2)

    def test_or_and_operator(self):
        """ test or and operator """
        query_string = '{"filter" : {"or" : { "name" : "Jhon", "lastname" : "Galt" }, "and" : { "uid" : "19571957" } } }'
        assert(elastic_query(User, query_string, session).count() == 1)

unittest.main()