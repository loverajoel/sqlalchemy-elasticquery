import unittest
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_elasticquery import elastic_query
from flask import Flask

Base = declarative_base()


class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return str(self.id)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    uid = Column(Integer)
    city_id = Column(Integer, ForeignKey(City.id))
    city = relationship(City)

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
        session._model_changes = {}

        Base.metadata.create_all(bind=engine)

        session.add_all([
            User(name='Jhon', lastname='Galt', uid='19571957', city_id=1),
            User(name='Steve', lastname='Jobs', uid='20092009', city_id=2),
            User(name='Iron', lastname='Man', uid='19571957', city_id=1),
            City(name='Cordoba'),
            City(name='New York')
        ])
        session.commit()

    def test_setup_is_ok(self):
        """ Demo test """
        assert(session.query(User).count() == 3)

    def test_simple_query(self):
        """ test simple query """
        query_string = '{"filter" : {"uid" : {"like" : "%1957%"} } }'
        assert(elastic_query(User, query_string, session).count() == 2)
        query_string = '{"filter" : {"name" : {"like" : "%Jho%"}, "lastname" : "Galt" } }'
        assert(elastic_query(User, query_string, session).count() == 1)

    def test_and_operator(self):
        """ test and operator """
        query_string = \
            '{"filter" : {"and" : {"name" : {"like" : "%Jho%"}, "lastname" : "Galt", "uid" : {"like" : "%1957%"} } } }'
        assert(elastic_query(User, query_string, session).count() == 1)

    def test_or_operator(self):
        """ test or operator """
        query_string = \
            '{"filter" : {"or" : { "name" : "Jobs", "lastname" : "Man", "uid" : "19571957" } } }'
        assert(elastic_query(User, query_string, session).count() == 2)

    def test_or_and_operator(self):
        """ test or and operator """
        query_string = \
            '{"filter" : {"or" : { "name" : "Jhon", "lastname" : "Galt" }, "and" : { "uid" : "19571957" } } }'
        assert(elastic_query(User, query_string, session).count() == 1)

    def test_sorting(self):
        """ test operator levels """
        query_string = \
            '{"filter" : {"or" : { "name" : "Jhon", "lastname" : "Man" } }, "sort": { "name" : "asc" } }'
        results = elastic_query(User, query_string, session).all()
        assert(results[0].name == 'Iron')

    def test_in_operator(self):
        """ test operator in """
        query_string = '{"filter" : {"name" : {"in" : ["Jhon", "Peter", "Iron"] } } }'
        assert(elastic_query(User, query_string, session).count() == 2)

        query_string = '{"filter" : {"name" : {"in" :["Jhon", "Peter", "Iron"]}, "lastname" : "Galt" } }'
        assert(elastic_query(User, query_string, session).count() == 1)

    def test_flask(self):
        app = Flask(__name__)
        db = SQLAlchemy(app)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        class Cities(db.Model):
            __tablename__ = 'users'

            id = Column(Integer, primary_key=True)
            name = Column(String)
            population = Column(Integer)

            def __init__(self, name, population):
                self.name = name
                self.population = population
                
        app.config['TESTING'] = True
        app = app.test_client()
        db.create_all()

        city = Cities("Cordoba", 1000000)
        db.session.add(city)
        city = Cities("Rafaela", 99000)
        db.session.add(city)
        db.session.commit()

        query_string = '{ "sort": { "population" : "desc" } }'
        results = elastic_query(Cities, query_string)
        assert(results[0].name == 'Cordoba')

    def test_allow_fields_option(self):
        """ test allow_fields option """
        query_string = '{"filter" : {"or" : { "name" : "Jhon", "lastname" : "Man" } }, "sort": { "name" : "asc" } }'
        enabled_fields = ['name']
        results = elastic_query(User, query_string, session, enabled_fields=enabled_fields).all()
        assert(results[0].name == 'Jhon')

    def test_search_for_levels(self):
        """ test search for levels """
        query_string = \
            '{"filter" : {"or" : { "city.name" : "New York", "lastname" : "Man" } }, "sort": { "name" : "asc" } }'
        results = elastic_query(User, query_string, session).all()
        assert(results[0].name == 'Iron')

        query_string = '{"filter" : { "city.name" : "New York" } }'
        results = elastic_query(User, query_string, session).all()
        assert(results[0].name == 'Steve')

        query_string = '{"filter" : { "city.name" : {"like" : "%New%"} } }'
        results = elastic_query(User, query_string, session).all()
        assert(results[0].name == 'Steve')


unittest.main()
