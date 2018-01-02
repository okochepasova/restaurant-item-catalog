import configuration

# DataBase Session
from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify

app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User, getEngine

# Verification
import re

# Login Session
from flask import session as login_session
import random, string

# Third Party Connection
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

from flask import make_response
import requests

# Extra
from flask import send_from_directory
import os


secrets_path = configuration.secrets_path
CLIENT_ID = json.loads(
    open(secrets_path, 'r').read())['web']['client_id']

# Variables
engine = getEngine()
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
db_session = DBSession()

rest = db_session.query(Restaurant)
menu = db_session.query(MenuItem)
user = db_session.query(User)


# App Routes
@app.route('/favicon.ico', methods=['GET','POST'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Create a state token to prevent request forgery.
# Store it in the session for later validation.
@app.route('/login')
def showLogin(methods=['GET','POST']):
    if request.method == 'GET':
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
            for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state)
    else:
        return 'The current session state is %s'%login_session['state']

#
# G-Connect
#
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Fail
    if request.args.get('state') != login_session['state']:
        return my_response(json.dumps('Invalid state parameter.'), 401)

    # Success
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(secrets_path, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        return my_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)

    access_token = credentials.access_token
    gplus_id = credentials.id_token['sub']
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'%
        access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # Check that the access token is valid.
    if result.get('error') is not None:
        return my_response(json.dumps(result.get('error')), 500)

    elif result['user_id'] != gplus_id:
        return my_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)

    elif result['issued_to'] != CLIENT_ID:
        print "Token's client ID does not match app's."
        return my_response(
            json.dumps("Token's client ID does not match app's."), 401)

    # See if the user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return my_response(
            json.dumps('Current user is already connected.'), 200)

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if the user exists. If not, make a new user.
    # Store the user id in the login session
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Closing
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

#
# DISCONNECT - Revoke a current user's token and reset their login_session.
#
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        return my_response(json.dumps('Current user not connected.'), 401)

    # Execute HTTP GET request to revoke current token.
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # For whatever reason, the given token was invalid.
    if result['status'] != '200':
        return my_response(
            json.dumps('Failed to revoke token for given user.'), 400)

# Facebook Connect
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        return my_response(json.dumps('Invalid state parameter.'), 401)
    access_token = request.data

    # Exchange client token for longer-lived server-side token with GET 
    # /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}
    # &client_secret={app-secrets}&fb_exchange_token={short-lived-token}
    app_id = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oath/access_token?grant_type='
    url += 'fb_exchange_token&client_id=%s&client_secret='%app_id
    url += '%s&fb_exchange_token=%s'%(app_secret,access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = 'https://graph.facebook.com/v2.8/me'
    # Strip expire tag from access token
    token = resut.split('&')[0]

    url = 'https://graph.facebook.com/v2.8/me?%s'%token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    # Store Data 
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']


    # Get user Picture
    url = 'https://graph.facebook.com/v2.8/me/picture?%s'%token
    url += '&redirect=0&height=200&width=200'
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']

    # See if the user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Closing
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# Facebook Disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions'%facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

# DISCONNECT
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        # Logging Out
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token'] 

        elif login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        # Delete
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        # Closing
        flash('You have successfully logged out.')
        return redirect(url_for('showRestaurants'))
    else:
        flash('You are not logged in.')
        return redirect(url_for('showRestaurants'))


# Making an API Endpoint (GET Request)
@app.route('/restaurant/JSON')
def restaurantsJSON():
    return jsonify(Restaurants=[r.serialize for r in rest.all()])

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    try:
        r1 = getRestaurant(restaurant_id)
        items = getMenuItems(restaurant_id)
        return jsonify(MenuItems=[i.serialize for i in items])
    except:
        return jsonify(MenuItems=None)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    try:
        item = getMenuItem(menu_id)
        if item.restaurant_id == restaurant_id:
            return jsonify(MenuItem = item.serialize)
        else:
            return jsonify(MenuItem=None)
    except:
        return jsonify(MenuItem=None)


# Body
#
# Show all Restaurants
#
@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
    if 'username' not in login_session:
        return render_template('restaurants.html', list=rest.all())
    else:
        return render_template('restaurants.html', list=rest.all(),
            user_id=login_session['user_id'])

#
# Create a new Restaurant
#
@app.route('/restaurant/new/', methods=['GET','POST'])
def newRestaurant():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        # Variables
        name = request.form['name']

        # Body
        if not name:
            flash('Empty Field.')
            return render_template('newEditRestaurant.html', action='Create')
        # Creating
        newItem = Restaurant(name=safe(name), user_id=login_session['user_id'])
        db_session.add(newItem)
        db_session.commit()
        flash('New Restaurant created!')

        # Closing
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newEditRestaurant.html', action='Create')

#
# Edit a Restaurant
#
@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    try:
        # Variables
        editItem = getRestaurant(restaurant_id)
        if editItem.user_id != login_session['user_id']:
            flash('You do not have authorization to edit %s.'%editItem.name)
            return redirect(url_for('showRestaurants'))

        # Body
        if request.method == 'POST':
            name = request.form['name']
            if not name:
                return render_template('newEditRestaurant.html', rest=editItem,
                    action='Edit')
            elif name == editItem.name:
                return redirect(url_for('showRestaurants'))
            # Updating
            editItem.name = safe(name)
            db_session.commit()
            flash('Restaurant was Edited.')

            # Closing
            return redirect(url_for('showRestaurants'))
        else:
            return render_template('newEditRestaurant.html', item=editItem,
                restaurant_id=restaurant_id)
    except:
        error()

#
# Delete a Restaurant
#
@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    try:
        delItem = getRestaurant(restaurant_id)
        if delItem.user_id != login_session['user_id']:
            flash('You do not have authorization to delete %s.'%delItem.name)
            return redirect(url_for('showRestaurants'))

        return '<title>Restaurant</title>\n<h1>Delete</h1>\n'

        if request.method == 'POST':
            #Deleting
            with getMenuItems(restaurant_id) as items:
                for i in items:
                    db_session.delete(i)
            db_session.delete(delItem)
            db_session.commit()
            flash('Restaurant Successfully Deleted.')

            # Closing
            return redirect(url_for('showRestaurants'))
        else:
            return render_template('deleteRestaurant.html', rest=delItem)
    except:
        return error()

#
# List of MenuItems
#
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    try:
        r1 = getRestaurant(restaurant_id)
        items = getMenuItems(restaurant_id)
        creator = getUserInfo(r1.user_id)

        if 'username' not in login_session:
            return render_template('menu.html', rest=r1, items=items,
                creator=creator)
        else:
            return render_template('menu.html', rest=r1, items=items,
                user_id=login_session['user_id'], creator=creator)
    except:
        return error()

#
# A new MenuItem
#
@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    try:
        r1 = getRestaurant(restaurant_id)
        if r1.user_id != login_session['user_id']:
            flash('You do not have authorization to add items to %s.'%r1.name)
            return redirect(url_for('showMenu', restaurant_id=r1.id))
    except:
        return error()

    if request.method == 'POST':
        # Variables
        name = request.form['name']
        price = request.form['price']
        desc = request.form['description']
        course = request.form['course']
        user_id = login_session['user_id']

        # Body
        if not name or not price or not desc or not course:
            flash('Empty Field.')
            return render_template('newEditMenuItem.html',action='Create',
                restaurant_id=restaurant_id)

        if not valid_price(price):
            flash('Incorrect price format.')
            return render_template('newEditMenuItem.html',action='Create',
                restaurant_id=restaurant_id)

        newItem = MenuItem(name=safe(name), price=price, course=course,
            description=safe(desc), restaurant_id=restaurant_id,
            user_id=user_id)
        db_session.add(newItem)
        db_session.commit()
        flash('New %s Created.'%newItem.name)

        # Closing
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newEditMenuItem.html',action='Create',
            restaurant_id=restaurant_id)

#
# Edit a MenuItem
#
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/',
    methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    try:
        # Variables
        r1 = getRestaurant(restaurant_id)
        editItem = getMenuItem(menu_id)
        if editItem.user_id != login_session['user_id']:
            flash('You do not have authorization to edit %s.'%editItem.name)
            return redirect(url_for('showMenu', restaurant_id=r1.id))

        elif editItem.restaurant_id != r1.id:
            flash('%s is not part of %s.'%(editItem.name, r1.name))
            return redirect(url_for('showMenu', restaurant_id=r1.id))

        if request.method == 'POST':
            # Variables
            name = request.form['name']
            price = request.form['price']
            desc = request.form['description']
            course = request.form['course']

            # Fail
            if not name or not price or not desc or not course:
                flash('Empty Field.')
                return render_template('newEditMenuItem.html',item=editItem,
                    restaurant_id=r1.id, action='Edit')
            # Succsess
            if valid_price(price):
                editItem.price = price
            else:
                flash('Incorrect price format.')
                return render_template('newEditMenuItem.html',item=editItem,
                    restaurant_id=r1.id, action='Edit')

            editItem.name = safe(name)
            editItem.description = safe(desc)
            editItem.course = course
            db_session.commit()
            flash('%s Successfully Edited.'%name)

            # Closing
            return redirect(url_for('showMenu', restaurant_id=r1.id))
        else:
            return render_template('newEditMenuItem.html', item=editItem,
                restaurant_id=r1.id, action='Edit')
    except:
        return error()

#
# Delete a MenuItem
#
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/',
    methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')

    try:
        r1 = getRestaurant(restaurant_id)
        delItem = getMenuItem(menu_id)
        # Varification
        if delItem.user_id != login_session['user_id']:
            flash('You do not have authorization to delete %s.'%delItem.name)
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))
			
        elif delItem.restaurant_id != r1.id:
            flash('%s is not part of %s.'%(delItem.name, r1.name))
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))

        if request.method == 'POST':
            flash('%s is deleted.'%delItem.name)
            db_session.delete(delItem)
            db_session.commit()

            # Closing
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))
        else:
            return render_template('deleteMenuItem.html', restaurant_id=restaurant_id,
                item=delItem)
    except:
        return error()


#
# Methods
#
def safe(name):
    word = []
    for c in name:
        if c == '"': word += '&#34;'
        elif c == "'": word += '&#39;'
        elif c == '(': word += '&#40;'
        elif c == ')': word += '&#41;'
        elif c == "/": word += '&#47;'
        elif c == '<': word += '&#60;'
        elif c == '>': word += '&#62;'
        elif c == '\\': word += '&#92;'
        else: word += c
    return ''.join(word)

def valid_price(price):
    PRICE_RE = re.compile(r"^\$\d+\.\d{2}$")
    return PRICE_RE.match(price)

def error():
    return my_response(json.dumps(
        'Such a Restaurant, MenuItem, or User does not exist.'), 404)

def my_response(string, code):
    response = make_response(string, code)
    response.headers['Content-Type'] = 'application/json'
    return response

# User Methods
def createUser(login_session):
    newUser = User(name=login_session['username'],email=login_session['email'],
        picture=login_session['picture'])
    db_session.add(newUser)
    db_session.commit()
    u = user.filter(User.email == login_session['email']).one()
    return u.id()

def getUserInfo(user_id):
    try:
        u = user.filter(User.id == user_id).one()
        return u
    except:
        return None

def getUserID(email):
    try:
        u = user.filter(User.email == email).one()
        return u.id
    except:
        return None

# Get Methods
def getRestaurant(r_id):
    return rest.filter(Restaurant.id == r_id).one()

def getMenuItem(m_id):
    return menu.filter(MenuItem.id == m_id).one()

def getMenuItems(r_id):
    return menu.filter(MenuItem.restaurant_id == r_id).all()
