from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Menu"

from flask import session as login_session
import random, string

engine = create_engine('sqlite:///catalog_database.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()



# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print(state)
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token


    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "url sent for API access:%s"% url
    print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


#Right now it is just showing the first one and not a list
@app.route('/categories/<int:Category_id>/JSON')
def CategoryListJSON(Category_id):
    category = session.query(Category).filter_by(id=Category_id).one()
    items = session.query(Item).filter_by(id=Category_id).all()
    return jsonify(Items=[i.serialize for i in items])


##Need to fix right now just showing the first one
@app.route('/categories/<int:Category_id>/<int:item_id>/JSON')
def itemJSON(Category_id, item_id):
    item = session.query(Item).filter_by(Category_id = Category_id).one()
    return jsonify(Item=item.serialize)


@app.route("/")
def application():
    #newUser = User(id = 1, name = "daniel", email = "danielspottiswood@gmail.com")
    #newcategory = Category(id = 1, name = "Cleaning")
    #session.add(newUser)
    #session.commit()
    #session.add(newcategory)
    #session.commit()
    #newItem = Item(name = "swiffer", description="new swiffer",price="100",condition="good", Category_id = 1, User_id=1)
    #session.add(newItem)
    #session.commit()
    items = session.query(Item).all()
    print(items[0].User_id)
    categories = session.query(Category).all()
    return render_template("home.html", Categories = categories)

@app.route('/categories/<int:Category_id>/')
def categoryitems(Category_id):
    category = session.query(Category).filter_by(id=Category_id).one()
    items = session.query(Item).filter_by(Category_id= Category_id)
    return render_template('Category.html', items = items, Category = category, Category_id = Category_id)

@app.route('/categories/<int:Category_id>/new', methods =['Get','Post'])
def newCategoryItem(Category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Item(name = request.form['name'], description=request.form['description'],price=request.form['price'],condition=request.form['condition'], Category_id = Category_id, user_id=login_session['User_id'])
        session.add(newItem)
        session.commit()
        print("Committed")
        return redirect(url_for("categoryitems", Category_id = Category_id))
    else:
        return render_template('newcategoryitem.html', Category_id = Category_id, Category = Category)

@app.route('/categories/<int:Category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editCategoryItem(Category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['condition']:
            editedItem.condition = request.form['condition']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('categoryitems', Category_id=Category_id))
    else:
        return render_template(
            'editCategoryItem.html', Category_id=Category_id, item_id=item_id, item = editedItem)

@app.route('/categories/<int:Category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteCategoryItem(Category_id, item_id):
    #if 'username' not in login_session:
    #    return redirect('/login')
    deleteItem = session.query(Item).filter_by(id=item_id).one()
    if request.method =='POST':
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('categoryitems', Category_id = Category_id))
    else:
        return render_template('deleteconfirmation.html', Category_id = Category_id, item=deleteItem)


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
