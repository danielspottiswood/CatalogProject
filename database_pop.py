from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
app = Flask(__name__)
from flask import session as login_session
import random, string

engine = create_engine('sqlite:///catalog_database.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

newUser1 = User(id = 1, name = "Michael", email = "michael@gmail.com")
session.add(newUser1)
newUser2 = User(id = 2, name = "Daniel", email = "danielspottiswood@gmail.com")
session.add(newUser2)
newcategory1 = Category(id = 1, name = "Cleaning")
session.add(newcategory1)
newcategory2 = Category(id = 2, name = "Entertainment")
session.add(newcategory2)
newcategory3 = Category(id = 3, name = "Tools")
session.add(newcategory3)
session.commit()
newItem1 = Item(name = "Swiffer", description="High Tech Cleaning Supply",price="10",condition="good", Category_id = 1, User_id=1)
session.add(newItem1)
newItem2 = Item(name = "TV", description="Plasma Flat Screen TV Samsung",price="70",condition="great", Category_id = 2, User_id=2)
session.add(newItem2)
newItem3 = Item(name = "Hammer", description="12 inch Hammer",price="12",condition="poor", Category_id = 3, User_id=2)
session.add(newItem3)
session.commit()
