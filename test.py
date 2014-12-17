import unittest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_elasticquery import elastic_query

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
        User(name='Joel', lastname='Lovera', uid='34755467'),
        User(name='Joel1', lastname='Lovera2', uid='34755468'),
        User(name='Joel2', lastname='Lovera3', uid='34755469')
        ])
        session.commit()

    def tearDown(self):
        """ Remove all setup """
        # db.session.remove()
        # db.drop_all()
        pass

    def test_setup_is_ok(self):
        """ Demo test """
        assert(session.query(User).count() == 3)

    def test_and(self):
        query_string = '{"filter" : {"and" : {"name" : {"like" : "joel"}, "lastname" : "joel", "uid" : {"like" : "joel"} } } }'
        elastic_query(User, query_string, session)

unittest.main()