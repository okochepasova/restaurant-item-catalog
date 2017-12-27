# CONFIGURATION
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


# Classes
class User(Base):
    # Table
    __tablename__ = 'user'

    # Mapper
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

    email = Column(String(250), nullable = False)
    picture = Column(String(250))

    # Methods
    @property
    def serialize(self):
        '''Return object data in easily serializeable format'''
        return {
            'name' : self.name,
            'id' : self.id,
            'email' : self.email,
            'picture' : self.picture
        }

class Restaurant(Base):
    # Table
    __tablename__ = 'restaurant'

    # Mapper
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Methods
    @property
    def serialize(self):
        '''Return object data in easily serializeable format'''
        return {
            'name' : self.name,
            'id' : self.id,
            'user_id' : self.user_id
        }

class MenuItem(Base):
    # Table
    __tablename__ = 'menu_item'

    # Mapper
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))

    # Foreign Key
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Methods
    @property
    def serialize(self):
        '''Return object data in easily serializeable format'''
        return {
            'name' : self.name,
            'id' : self.id,
            'course' : self.course,
            'description' : self.description,
            'price' : self.price,
            'restaurant_id' : self.restaurant_id,
            'user_id' : self.user_id
        }


####### insert at the end of file #######
engine = create_engine('postgresql://grader:udacity@localhost:5432/grader')
Base.metadata.create_all(engine)

def getEngine():
    return engine;
