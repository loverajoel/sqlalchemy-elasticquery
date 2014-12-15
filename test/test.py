from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_elastiquery import elastic_query

Base = declarative_base()

def prepare_enviroment():
    global engine
    engine = create_engine('sqlite:///:memory:', echo=True)
    global Session
    Session = sessionmaker(bind=engine)
    global session
    session = Session()

# Models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    uid = Column(Integer)

    def __repr__(self):
        return str(self.id)

def create_tables():
    Base.metadata.create_all(bind=engine)

def create_data():
    # ed_user = User(name='Joel', lastname='Lovera', uid='34755467')
    # session.add(ed_user)
    # session.commit()
    session.add_all([
        User(name='Joel', lastname='Lovera', uid='34755467'),
        User(name='Joel1', lastname='Lovera2', uid='34755468'),
        User(name='Joel2', lastname='Lovera3', uid='34755469')
        ])
    session.commit()


prepare_enviroment()
create_tables()
create_data()

print session.query(User).all()