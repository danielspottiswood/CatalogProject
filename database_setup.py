import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, autoincrement = True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Category(Base):
    __tablename__ = 'Category'
    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String(80), nullable = False)
    #user_id = Column(Integer, ForeignKey('User.id'))
    #User = relationship(User)
    @property
    def serialize(self):
        return {
            'name' : self.name,
            'id' : self.id,
            #'user_id' : self.user_id
            #'description' = self.description,
            #'condition' = self.condition,
            #'price' = self.price
        }

class Item(Base):
    __tablename__ = 'Item'
    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String(80), nullable = False)
    description = Column(String(200))
    condition = Column(String(100), nullable = False)
    price = Column(String(10))
    Category_id = Column(Integer, ForeignKey('Category.id'))
    Category = relationship(Category)
    User_id = Column(Integer, ForeignKey('User.id'))
    User = relationship(User)
    @property
    def serialize(self):

        return {
            'name' : self.name,
            'id' : self.id
            #'description' = self.description,
            #'condition' = self.condition,
            #'price' = self.price
            }

engine = create_engine('sqlite:///catalog_database.db')

Base.metadata.create_all(engine)
