# DataBase Session
from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify

app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Verification
import re


# Variables
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

rest = session.query(Restaurant)
menu = session.query(MenuItem)


# Making an API Endpoint (GET Request)
@app.route('/restaurant/JSON')
def restaurantsJSON():
    return jsonify(Restaurants=[r.serialize for r in rest.all()])

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    try:
        r1 = rest.filter(Restaurant.id == restaurant_id).one()
        items = menu.filter(MenuItem.restaurant_id == r1.id).all()
        return jsonify(MenuItems=[i.serialize for i in items])
    except:
        return jsonify(MenuItems=None)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    try:
        item = menu.filter(MenuItem.id == menu_id).one()
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
    #return 'This page will show all my restaurants'
    return render_template('restaurants.html', list=rest.all())

#
# Create a new Restaurant
#
@app.route('/restaurant/new/')
def newRestaurant(methods=['GET','POST']):
    if request.method == 'POST':
        name = request.form['name']
        if not name:
            return render_template('newEditRestaurant.html', action='Create')

        # Creating
        r1 = Restaurant(name=safe(name))
        session.add(r1)
        session.commit()
        flash('New Restaurant Created.')

        # Closing
        redirect(url_for('showRestaurants'))
    else:
        return render_template('newEditRestaurant.html', action='Create')

#
# Edit a Restaurant
#
@app.route('/restaurant/<int:restaurant_id>/edit/')
def editRestaurant(restaurant_id, methods=['GET','POST']):
    try:
        r1 = rest.filter(Restaurant.id == restaurant_id).one()
        if request.method == 'POST':
            name = request.form['name']
            if not name:
                return render_template('newEditRestaurant.html', rest=r1,
                                       action='Create')
            # Editing
            r1.name = safe(name)
            session.commit()
            flash('Restaurant Successfully Edited.')

            # Closing
            redirect(url_for('showRestaurants'))
        else:
            return render_template('newEditRestaurant.html', action='Create',
                                   rest=r1)
    except:
        return error_rest(restaurant_id)

#
# Delete a Restaurant
#
@app.route('/restaurant/<int:restaurant_id>/delete/')
def deleteRestaurant(restaurant_id, methods=['GET','POST']):
    try:
        r1 = rest.filter(Restaurant.id == restaurant_id).one()
        if request.method == 'POST':
            # Deleting
            session.delete(r1)
            session.commit()
            flash('Restaurant Successfully Deleted.')

            # Closing
            redirect(url_for('showRestaurants'))
        else:
            return render_template('deleteRestaurant.html', rest=r1)
    except:
        return error_rest(restaurant_id)

#
# Show a Restaurant Menu
#
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    try:
        r1 = rest.filter(Restaurant.id == restaurant_id).one()
        items = menu.filter(MenuItem.restaurant_id == r1.id).all()
        return render_template('menu.html', restaurant=r1, items=items)
    except:
        return error_rest(restaurant_id)

#
# Create a new MenuItem
#
@app.route('/restaurant/<int:restaurant_id>/menu/new/')
def newMenuItem(restaurant_id, methods=['GET','POST']):
    try:
        r1 = rest.filter(Restaurant.id == restaurant_id).one()
        if request.method == 'POST':
            # Variables
            name = request.form['name']
            price = request.form['price']
            desc = request.form['description']
            course = request.form['course']

            # Body
            if not name or not price or not desc or not course:
                return render_template('newEditMenuItem.html',
                                       restaurant_id=restaurant_id)
            newItem = MenuItem(name=safe(name),price=valid_price(price),
                               description=safe(desc),restaurant_id=restaurant_id)
            session.add(newItem)
            session.commit()
            flash('New Menu Item Created.')

            # Closing
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))
        else:
            return render_template('newEditMenuItem.html',
                                   restaurant_id=restaurant_id)
    except:
        return error_rest(restaurant_id)

#
# Edit a MenuItem
#
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id, methods=['GET','POST']):
    try:
        editItem = menu.filter(MenuItem.id == menu_id).one()
        if editItem.restaurant_id == restaurant_id:
            if request.method == 'GET':
                return render_template('newEditMenuItem.html', item=editItem,
                                       restaurant_id=restaurant_id)
            elif request.method == 'POST':
                # Variables
                name = request.form['name']
                price = request.form['price']
                desc = request.form['description']
                course = request.form['course']

                # Fail
                if not name or not price or not desc or not course:
                    return render_template('newEditMenuItem.html',item=editItem,
                                           restaurant_id=restaurant_id)
                # Succsess
                editItem.name = safe(name)
                editItem.price = valid_price(price)
                editItem.description = safe(desc)
                editItem.course = course
                session.commit()
                flash('Menu Item Successfully Edited.')

                # Closing
                return redirect(url_for('showMenu', restaurant_id=restaurant_id))
        else:
            return error_rest(restaurant_id)
    except:
        return error_menu(menu_id)

#
# Delete a MenuItem
#
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id, methods=['GET','POST']):
    try:
        delItem = menu.filter(MenuItem.id == menu_id).one()
        if delItem.restaurant_id == restaurant_id:
            if request.method == 'GET':
                return render_template('deleteMenuItem.html', item=delItem,
                                       restaurant_id=restaurant_id)
            elif request.method == 'POST':
                #Deleting
                session.delete(delItem)
                session.commit()
                flash('Menu Item Successfully Deleted.')

                # Closing
                return redirect(url_for('showMenu', restaurant_id=restaurant_id))
        else:
            return error_rest(restaurant_id)
    except:
        return error_menu(menu_id)


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
        elif c == '/': word += '&#47;'
        elif c == '<': word += '&#60;'
        elif c == '>': word += '&#62;'
        elif c == '\\': word += '&#92;'
        else: word += c
    return ''.join(word)

def valid_price(price):
    PRICE_RE = re.compile(r"^$[0-9]+.[0-9]{2}")
    return PRICE_RE.match(price)

def error_rest(r_id):
    return 'Error 404:\nCould not find Restaurant with id of %d' % r_id

def error_menu(m_id):
    return 'Error 404:\nCould not find Menu Item with id of %d' % m_id


# MAIN
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
